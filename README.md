# Aurora Fullstack SaaS - Modern SaaS Web Application
# Tech Stack: Next.js 14, React Server Components, TypeScript, FastAPI, GraphQL

## Project Structure

```
aurora-fullstack-saas/
├── apps/
│   ├── shell-host/              # Micro-frontend shell
│   ├── identity-mfe/             # Identity/authentication MFE
│   ├── dashboard-mfe/           # Dashboard MFE
│   ├── tasks-mfe/               # Task management MFE
│   ├── admin-mfe/               # Admin panel MFE
│   └── billing-mfe/             # Billing MFE
├── packages/
│   ├── ui-components/           # Shared UI components (shadcn/ui)
│   ├── shared-utils/            # Shared utilities
│   └── shared-types/            # Shared TypeScript types
├── services/
│   ├── api-gateway/             # GraphQL API Gateway
│   ├── auth-gateway/            # Authentication Gateway
│   ├── realtime-gateway/        # Real-time WebSocket Gateway
│   ├── tasks-service/           # Task domain service
│   ├── users-service/           # User domain service
│   └── billing-service/         # Billing domain service
├── infrastructure/
│   ├── terraform/               # Infrastructure as Code
│   └── kubernetes/              # K8s manifests
└── tests/                       # Test files
```

## Getting Started

### Prerequisites
- Node.js 18+
- Python 3.11+
- Docker & Docker Compose
- Azure CLI

### Development Setup

1. Install dependencies:
```bash
# Frontend
cd apps/shell-host && npm install

# Backend
cd services/api-gateway && pip install -r requirements.txt
```

2. Start local development:
```bash
# Start all services
docker-compose up -d

# Or start individually
npm run dev --workspace=apps/shell-host
```

### Environment Variables

See `.env.example` for required environment variables.

## Architecture

- **Micro-frontends**: Independent deployment of UI components using Module Federation
- **BFF Pattern**: Backend-for-Frontend per micro-frontend
- **Multi-tenancy**: Shared infrastructure, isolated data
- **Real-time**: Collaborative features with WebSockets
- **Authentication**: Auth.js v5 with JWT, OAuth2, WebAuthn

## Deployment

See `infrastructure/terraform` for Azure infrastructure deployment.

## Testing

```bash
# Unit tests
npm run test

# E2E tests
npm run test:e2e

# Lint
npm run lint
```

## License

Proprietary - Dulux Tech
