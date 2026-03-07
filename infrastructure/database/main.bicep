// Azure Bicep Template - Azure SQL Database (Multi-tenant)
// Aurora Fullstack SaaS Platform

@description('Environment name')
param environment string = 'prod'

@description('Azure region')
param location string = resourceGroup().location

@description('SQL Server name')
param sqlServerName string = 'sql-aurora-${environment}'

@description('Administrator login')
param administratorLogin string = 'sqladmin'

@description('Administrator password')
@secure()
param administratorPassword string

// SQL Server
resource sqlServer 'Microsoft.Sql/servers@2022-11-01' = {
  name: sqlServerName
  location: location
  properties: {
    administratorLogin: administratorLogin
    administratorPassword: administratorPassword
    version: '12.0'
    minimalTlsVersion: '1.2'
    publicNetworkAccess: 'Enabled'
    firewallRules: [
      {
        name: 'AllowAllAzureIPs'
        properties: {
          startIpAddress: '0.0.0.0'
          endIpAddress: '0.0.0.0'
        }
      }
    ]
  }
}

// Tenant Database
resource tenantDatabase 'Microsoft.Sql/servers/databases@2022-11-01' = {
  parent: sqlServer
  name: 'aurora_tenants'
  location: location
  sku: {
    name: 'S0'
    tier: 'Standard'
    capacity: 10
  }
  properties: {
    collation: 'SQL_Latin1_General_CP1_CI_AS'
    maxSizeBytes: 5368709120
    catalogCollation: 'SQL_Latin1_General_CI_AS'
    zoneRedundant: false
    readScale: 'Disabled'
  }
}

// Shared Database (users, auth, billing)
resource sharedDatabase 'Microsoft.Sql/servers/databases@2022-11-01' = {
  parent: sqlServer
  name: 'aurora_shared'
  location: location
  sku: {
    name: 'S0'
    tier: 'Standard'
    capacity: 10
  }
  properties: {
    collation: 'SQL_Latin1_General_CP1_CI_AS'
    maxSizeBytes: 5368709120
  }
}

// Threat Detection
resource threatDetection 'Microsoft.Sql/servers/databases/securityAlertPolicies@2022-11-01' = {
  parent: tenantDatabase
  name: 'Default'
  properties: {
    state: 'Enabled'
    emailAddresses: 'security@aurora-saas.io'
    retentionDays: 30
  }
}

output sqlServerName string = sqlServer.name
output sqlServerFqdn string = sqlServer.properties.fullyQualifiedDomainName
output tenantDbConnection string = 'Server=tcp:${sqlServer.properties.fullyQualifiedDomainName},1433;Database=aurora_tenants;User Id=${administratorLogin}@${sqlServerName};Password=${administratorPassword};Encrypt=true;'
output sharedDbConnection string = 'Server=tcp:${sqlServer.properties.fullyQualifiedDomainName},1433;Database=aurora_shared;User Id=${administratorLogin}@${sqlServerName};Password=${administratorPassword};Encrypt=true;'
