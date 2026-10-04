# API Gateway

Centrale API gateway voor alle fleet services.

## Features

- Rate limiting
- Authentication
- Request routing
- Load balancing
- Monitoring

## Installatie

```bash
git clone https://github.com/itsdarklikehell/api-gateway.git
cd api-gateway
docker-compose up -d
```

## Gebruik

```bash
curl http://localhost:8080/health
curl http://localhost:8080/api/v1/status
```

## Licentie

MIT
