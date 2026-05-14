# Azure Microsoft Ecosystem - Veyra
@description('Environment name')
param environmentName string = 'veyra-azure-prod'

@description('Azure region')
param location string = resourceGroup().location

@description('Administrator password for PostgreSQL')
@secure()
param adminPassword string

@description('Docker image for the application')
param appImage string = 'veyra:latest'

@description('Microsoft 365 tenant ID')
param m365TenantId string

@description('Power BI workspace ID')
param powerBiWorkspaceId string

// Resource Group
resource rg 'Microsoft.Resources/resourceGroups@2021-04-01' = {
  name: environmentName
  location: location
  tags: {
    Environment = 'production'
    Application = 'Veyra'
    Provider = 'Azure'
    Role = 'Microsoft-Ecosystem'
  }
}

// Azure AD for Identity Management
resource aad 'Microsoft.Graph/directoryObjects@v1.0' = {
  displayName: 'Veyra Users'
  description: 'User group for Veyra application'
  mailNickname: 'veyra-users'
  securityEnabled = true
  mailEnabled = true
  
  tags: {
    Application = 'Veyra'
    Provider = 'Azure'
    Role = 'Microsoft-Ecosystem'
  }
}

// Container Registry for Docker Images
resource acr 'Microsoft.ContainerRegistry/registries@2023-01-01-preview' = {
  name: '${environmentName}acr'
  location: location
  resourceGroup: rg.name
  sku: {
    name: 'Premium'
  }
  adminUserEnabled = true
  
  tags: {
    Application = 'Veyra'
    Provider = 'Azure'
    Role = 'Microsoft-Ecosystem'
  }
}

// Log Analytics Workspace
resource la 'Microsoft.OperationalInsights/workspaces@2022-10-01' = {
  name: '${environmentName}-logs'
  location: location
  resourceGroup: rg.name
  properties: {
    sku: {
      name = 'PerGB2018'
    }
    retentionInDays: 30
  }
  
  tags: {
    Application = 'Veyra'
    Provider = 'Azure'
    Role = 'Microsoft-Ecosystem'
  }
}

// Container App Environment
resource cae 'Microsoft.App/managedEnvironments@2023-05-01' = {
  name: '${environmentName}-env'
  location: location
  resourceGroup: rg.name
  properties: {
    appLogsConfiguration: {
      destination: 'log-analytics'
      logAnalyticsConfiguration: {
        customerId: la.properties.customerId
        sharedKey: la.listKeys().keys[0].value
      }
    }
  }
  
  tags: {
    Application = 'Veyra'
    Provider = 'Azure'
    Role = 'Microsoft-Ecosystem'
  }
}

// Virtual Network for Container Apps
resource vnet 'Microsoft.Network/virtualNetworks@2021-02-01' = {
  name: '${environmentName}-vnet'
  location: location
  resourceGroup: rg.name
  properties: {
    addressSpace: {
      addressPrefixes: [
        '10.0.0.0/16'
      ]
    }
  }
  
  tags: {
    Application = 'Veyra'
    Provider = 'Azure'
    Role = 'Microsoft-Ecosystem'
  }
}

// Subnet for Container Apps
resource subnet 'Microsoft.Network/virtualNetworks/subnets@2021-02-01' = {
  parent: vnet
  name: 'container-apps-subnet'
  properties: {
    addressPrefix: '10.0.1.0/24'
    delegation: [
      {
        name: 'delegationContainerApp'
        properties: {
          serviceName: 'Microsoft.App/environments'
          actions: [
            'Microsoft.Network/virtualNetworks/subnets/action'
          ]
        }
      }
    ]
  }
  
  tags: {
    Application = 'Veyra'
    Provider = 'Azure'
    Role = 'Microsoft-Ecosystem'
  }
}

// Azure SQL - Enterprise Database
resource postgres 'Microsoft.DBforPostgreSQL/flexibleServers@2022-12-01' = {
  name: '${environmentName}-postgres'
  location: location
  resourceGroup: rg.name
  properties: {
    version: '15'
    administratorLogin: 'veyra'
    administratorLoginPassword: adminPassword
    storage: {
      storageSizeGB: 200
    }
    backup: {
      backupRetentionDays: 14
      geoRedundantBackup: 'Enabled'
    }
    highAvailability: {
      mode: 'ZoneRedundant'
    }
    network: {
      delegatedSubnetResourceId: subnet.id
    }
  }
  sku: {
    name: 'Standard_D4s_v3'
    tier: 'GeneralPurpose'
  }
  
  tags: {
    Application = 'Veyra'
    Provider = 'Azure'
    Role = 'Microsoft-Ecosystem'
  }
}

// Azure Cache for Redis
resource redis 'Microsoft.Cache/redis@2022-06-01' = {
  name: '${environmentName}-redis'
  location: location
  resourceGroup: rg.name
  properties: {
    sku: {
      name: 'Premium'
      family: 'P'
      capacity: 1
    }
    enableNonSslPort: false
    minimumTlsVersion: '1.2'
  }
  
  tags: {
    Application = 'Veyra'
    Provider = 'Azure'
    Role = 'Microsoft-Ecosystem'
  }
}

// Container App for Application Backend
resource ca 'Microsoft.App/containerApps@2023-05-01' = {
  name: '${environmentName}-api'
  location: location
  resourceGroup: rg.name
  properties: {
    managedEnvironmentId: cae.id
    configuration: {
      ingress: {
        external: true
        targetPort: 8000
        transport: 'http'
        allowInsecure: false
      }
      secrets: [
        {
          name: 'database-password'
          value: adminPassword
        }
      ]
      env: [
        {
          name: 'DATABASE_URL'
          value: 'postgresql://veyra:${adminPassword}@${postgres.properties.fullyQualifiedDomainName}:5432/veyra'
        }
        {
          name: 'REDIS_URL'
          value: 'redis://${redis.properties.hostName}:6379'
        }
        {
          name: 'AZURE_CLIENT_ID'
          value: azureApp.applicationId
        }
        {
          name: 'AZURE_TENANT_ID'
          value: tenant().tenantId
        }
        {
          name: 'POWER_BI_EMBED_URL'
          value: powerBiWorkspace.embedUrl
        }
      ]
    }
    template: {
      containers: [
        {
          image: appImage
          name: 'veyra-api'
          resources: {
            cpu: json('1')
            memory: '2Gi'
          }
          probe: {
            httpGet: {
              path: '/health'
              port: 8000
            }
            type: 'Liveness'
            initialDelaySeconds: 10
            periodSeconds: 30
          }
        }
      ]
      scale: {
        minReplicas: 2
        maxReplicas: 10
        rules: [
          {
            name: 'cpu-scale'
            custom: {
              type: 'http'
              metadata: {
                concurrentRequests: '100'
              }
            }
          }
        ]
      }
    }
  }
  
  tags: {
    Application = 'Veyra'
    Provider = 'Azure'
    Role = 'Microsoft-Ecosystem'
  }
}

// Power BI Workspace for Business Intelligence
resource powerBiWorkspace 'Microsoft.PowerBI/workspace@2020-06-01' = {
  name: '${environmentName}-analytics'
  location: location
  
  tags: {
    Application = 'Veyra'
    Provider = 'Azure'
    Role = 'Microsoft-Ecosystem'
  }
}

// Office 365 Integration
resource office365 'Microsoft.Graph/servicePrincipals@v1.0' = {
  displayName: 'Veyra Office Integration'
  description: 'Service principal for Office 365 integration'
  appId: azureApp.applicationId
  
  appRoles: [
    {
      allowedMemberTypes: [
        'Application'
      ]
      description: 'Read financial data from Office 365'
      displayName: 'Financial Data Reader'
      id: 'financial-data-reader'
      isEnabled: true
      value: 'financial-data-reader'
    }
  ]
}

// Front Door CDN for Global Distribution
resource fd 'Microsoft.Cdn/profiles@2021-06-01' = {
  name: '${environmentName}-fd'
  location: 'global'
  resourceGroup: rg.name
  sku: {
    name: 'Standard_AzureFrontDoor'
  }
  
  tags: {
    Application = 'Veyra'
    Provider = 'Azure'
    Role = 'Microsoft-Ecosystem'
  }
}

// Azure Functions for Serverless
resource functionApp 'Microsoft.Web/sites@2022-03-01' = {
  name: '${environmentName}-functions'
  location: location
  resourceGroup: rg.name
  kind: 'functionapp'
  
  properties: {
    serverFarmId: serverFarm.id
    siteConfig: {
      appSettings: [
        {
          name: 'FUNCTIONS_EXTENSION_VERSION'
          value: '~4'
        }
        {
          name: 'WEBSITE_RUN_FROM_PACKAGE'
          value: '1'
        }
        {
          name: 'FUNCTIONS_WORKER_RUNTIME'
          value: 'python'
        }
        {
          name: 'AzureWebJobsStorage'
          value: storageAccount.primaryConnectionString
        }
      ]
    }
  }
  
  tags: {
    Application = 'Veyra'
    Provider = 'Azure'
    Role = 'Microsoft-Ecosystem'
  }
}

// Application Registration for OAuth
resource azureApp 'Microsoft.Graph/applications@v1.0' = {
  displayName: 'Veyra'
  signInAudience = 'AzureADMyOrg'
  
  web: {
    redirectUris: [
      'https://veyra.azurewebsites.net/.auth/login/aad/callback'
    ]
  }
  
  requiredResourceAccess: [
    {
      resourceAppId = '00000003-0000-0000-c000-000000000000'
      resourceAccess: [
        {
          id: 'e1fe6dd8-ba31-4d61-89e7-8863946d1c19'
          type: 'Scope'
        }
      ]
    }
  ]
  
  tags: {
    Application = 'Veyra'
    Provider = 'Azure'
    Role = 'Microsoft-Ecosystem'
  }
}