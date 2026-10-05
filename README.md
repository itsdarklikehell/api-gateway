# API Gateway

Centrale API gateway voor alle fleet services.

## Status

**Huidige implementatie:** Minimalistische health-check gateway.

De gateway is momenteel een basisimplementatie met een `/health` endpoint.
Geplande features (rate limiting, authentication, request routing, load balancing, monitoring) zijn nog niet geïmplementeerd.

## Features

- [x] Health check endpoint (`/health`)
- [ ] Rate limiting
- [ ] Authentication
- [ ] Request routing
- [ ] Load balancing
- [ ] Monitoring

## Installatie

```bash
git clone https://github.com/itsdarklikehell/api-gateway.git
cd api-gateway
python3 gateway.py
```

De gateway start op `0.0.0.0:8080`.

## Gebruik

```bash
# Health check
curl http://localhost:8080/health
# Response: {"status": "ok"}
```

## Tests

```bash
python3 -m unittest test_gateway.py -v
```

## API

| Method | Path | Beschrijving |
|--------|------|--------------|
| GET | `/health` | Health check — retourneert `{"status": "ok"}` met HTTP 200 |
| GET | `*` | Onbekende paden retourneren HTTP 404 |

## Architectuur

```
gateway.py
  └── GatewayHandler (http.server.BaseHTTPRequestHandler)
        └── do_GET()
              ├── /health → 200 {"status": "ok"}
              └── * → 404
```

## Development

### Vereisten

- Python 3.9+

### Project structuur

```
api-gateway/
├── gateway.py           # Hoofdapplicatie
├── test_gateway.py      # Unit tests
├── requirements.txt     # Dependencies (momenteel leeg)
├── .github/workflows/
│   ├── ci.yml          # CI pipeline
│   └── gource.yml      # Gource visualisatie
└── README.md           # Dit bestand
```

## Licentie

MIT
