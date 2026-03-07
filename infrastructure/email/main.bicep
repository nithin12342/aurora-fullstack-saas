// Azure Bicep Template - SendGrid Email Configuration
// Aurora Fullstack SaaS Platform

@description('Environment name')
param environment string = 'prod'

@description('Azure region')
param location string = resourceGroup().location

@description('SendGrid API Key name in Key Vault')
param sendGridApiKeySecretName string = 'SendGridApiKey'

@description('Key Vault name')
param keyVaultName string = 'kv-aurora-${environment}'

@description('From email address')
param fromEmail string = 'noreply@aurora-saas.io'

@description('From display name')
param fromName string = 'Aurora SaaS'

// Get Key Vault reference
resource keyVault 'Microsoft.KeyVault/vaults@2023-02-01' existing = {
  name: keyVaultName
}

// App Service Plan for email worker
resource appServicePlan 'Microsoft.Web/serverfarms@2022-09-01' = {
  name: 'asp-aurora-email-${environment}'
  location: location
  sku: {
    name: 'Y1'
    tier: 'Dynamic'
    size: 'Y1'
    family: 'Y'
    capacity: 0
  }
  kind: 'functionapp'
  properties: {
    perSiteScaling: false
    elasticScaleEnabled: false
    maximumElasticWorkerCount: 1
  }
}

// Email Worker Function App
resource emailFunctionApp 'Microsoft.Web/sites@2022-09-01' = {
  name: 'func-aurora-email-${environment}'
  location: location
  kind: 'functionapp'
  identity: {
    type: 'SystemAssigned'
  }
  properties: {
    serverFarmId: appServicePlan.id
    httpsOnly: true
    siteConfig: {
      alwaysOn: false
      appSettings: [
        {
          name: 'AZURE_FUNCTIONS_ENVIRONMENT'
          value: environment
        }
        {
          name: 'FUNCTIONS_WORKER_RUNTIME'
          value: 'node'
        }
        {
          name: 'WEBSITE_NODE_DEFAULT_VERSION'
          value: '~18'
        }
        {
          name: 'SENDGRID_API_KEY'
          value: '@Microsoft.KeyVaultReference(${keyVault.id}, ${sendGridApiKeySecretName})'
        }
        {
          name: 'FROM_EMAIL'
          value: fromEmail
        }
        {
          name: 'FROM_NAME'
          value: fromName
        }
        {
          name: 'AZURE_KEY_VAULT_URI'
          value: keyVault.properties.vaultUri
        }
      ]
    }
  }
}

// Storage Account for function app
resource storageAccount 'Microsoft.Storage/storageAccounts@2023-01-01' = {
  name: 'stauroraemail${environment}'
  location: location
  kind: 'StorageV2'
  sku: {
    name: 'Standard_LRS'
  }
  properties: {
    supportsHttpsTrafficOnly: true
    minimumTlsVersion: 'TLS1_2'
  }
}

// Role Assignment for Key Vault access
resource keyVaultRoleAssignment 'Microsoft.Authorization/roleAssignments@2022-04-01' = {
  name: guid(subscription().id, emailFunctionApp.name, 'Key Vault Secrets User')
  scope: keyVault
  roleDefinitionId: '4633458b-17de-408a-b2d7-594bac65000a'
  principalId: emailFunctionApp.identity.principalId
  principalType: 'ServicePrincipal'
}

output emailFunctionAppName string = emailFunctionApp.name
output emailFunctionAppHostName string = emailFunctionApp.properties.defaultHostName
