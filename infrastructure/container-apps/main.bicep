// Azure Bicep Template - Azure Container Apps Environment
// Aurora Fullstack SaaS Platform

@description('Environment name')
param environment string = 'prod'

@description('Azure region')
param location string = resourceGroup().location

@description('Container Apps environment name')
param containerAppsEnvName string = 'env-aurora-${environment}'

@description('Log Analytics workspace name')
param logAnalyticsName string = 'law-aurora-${environment}'

@description('Application Insights name')
param appInsightsName string = 'ai-aurora-${environment}'

@description('VNet name')
param vnetName string = 'vnet-aurora-${environment}'

// Log Analytics Workspace
resource logAnalytics 'Microsoft.OperationalInsights/workspaces@2022-10-01' = {
  name: logAnalyticsName
  location: location
  properties: {
    sku: {
      name: 'PerGB2018'
    }
    retentionInDays: 30
    features: {
      searchVersion: 1
    }
  }
}

// Application Insights
resource appInsights 'Microsoft.Insights/components@2020-02-02' = {
  name: appInsightsName
  location: location
  kind: 'web'
  properties: {
    Application_Type: 'web'
    Request_Source: 'rest'
    RetentionInDays: 30
    publicNetworkAccessForIngestion: 'Enabled'
    publicNetworkAccessForQuery: 'Enabled'
    WorkspaceResourceId: logAnalytics.id
  }
}

// Virtual Network
resource vnet 'Microsoft.Network/virtualNetworks@2023-04-01' = {
  name: vnetName
  location: location
  addressSpace: {
    addressPrefixes: ['10.5.0.0/16']
  }
  subnets: [
    {
      name: 'snet-containerapps'
      addressPrefix: '10.5.1.0/24'
      delegations: [
        {
          name: 'Microsoft.App.environments'
          properties: {
            serviceName: 'Microsoft.App.environments'
          }
        }
      ]
    }
  ]
}

// Container Apps Environment
resource containerAppsEnv 'Microsoft.App/managedEnvironments@2023-05-01' = {
  name: containerAppsEnvName
  location: location
  properties: {
    appLogsConfiguration: {
      destination: 'log-analytics'
      logAnalyticsConfiguration: {
        customerId: logAnalytics.properties.customerId
        sharedKey: logAnalytics.listKeys().primarySharedKey
      }
    }
    vnetConfiguration: {
      internal: true
      subnetId: vnet.properties.subnets[0].id
    }
    workloadProfiles: [
      {
        name: 'Consumption'
        workloadProfileType: 'Consumption'
      }
      {
        name: 'D4s'
        workloadProfileType: 'Dedicated'
        minimumCount: 1
        maximumCount: 3
      }
    ]
  }
}

// Container App - API
resource apiContainerApp 'Microsoft.App/containerApps@2023-05-01' = {
  name: 'api-aurora'
  location: location
  properties: {
    managedEnvironmentId: containerAppsEnv.id
    configuration: {
      activeRevisionsMode: 'Single'
      ingress: {
        external: true
        targetPort: 8080
        transport: 'auto'
        allowInsecure: false
        customDomains: [
          {
            name: 'api.aurora-saas.io'
            bindingType: 'Sni'
            certificateId: ''
          }
        ]
      }
      registries: []
      secrets: [
        {
          name: 'container-registry-password'
          value: ''
        }
      ]
      ingressSettings: {
        clientAuthenticationMode: 'Istio'
      }
    }
    template: {
      containers: [
        {
          name: 'api'
          image: 'mcr.microsoft.com/azuredocs/containerapps-helloworld:latest'
          resources: {
            cpu: '1.0'
            memory: '2Gi'
          }
          env: [
            {
              name: 'NODE_ENV'
              value: 'production'
            }
            {
              name: 'APPINSIGHTS_INSTRUMENTATIONKEY'
              value: appInsights.properties.InstrumentationKey
              secretRef: 'appinsights-key'
            }
          ]
        }
      ]
      scale: {
        minReplicas: 1
        maxReplicas: 10
        rules: [
          {
            name: 'http-scaling'
            http: {}
          }
        ]
      }
    }
  }
}

// Container App - Web
resource webContainerApp 'Microsoft.App/containerApps@2023-05-01' = {
  name: 'web-aurora'
  location: location
  properties: {
    managedEnvironmentId: containerAppsEnv.id
    configuration: {
      activeRevisionsMode: 'Single'
      ingress: {
        external: true
        targetPort: 3000
        transport: 'auto'
        customDomains: [
          {
            name: 'app.aurora-saas.io'
            bindingType: 'Sni'
          }
        ]
      }
    }
    template: {
      containers: [
        {
          name: 'web'
          image: 'mcr.microsoft.com/azuredocs/containerapps-helloworld:latest'
          resources: {
            cpu: '0.5'
            memory: '1Gi'
          }
        }
      ]
      scale: {
        minReplicas: 1
        maxReplicas: 5
      }
    }
  }
}

output containerAppsEnvName string = containerAppsEnv.name
output containerAppsEnvId string = containerAppsEnv.id
output logAnalyticsCustomerId string = logAnalytics.properties.customerId
output appInsightsInstrumentationKey string = appInsights.properties.InstrumentationKey
