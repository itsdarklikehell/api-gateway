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

## :film_projector: Development visualization

Bekijk de [Gource development video](https://github.com/itsdarklikehell/api-gateway/releases) voor een visuele tijdlijn van de projectgeschiedenis.

Om de video lokaal te genereren:
```bash
gource -1920x1080 --auto-skip-seconds 1 -o gource.ppm
ffmpeg -y -r 60 -i gource.ppm -c:v libx264 -preset slow -crf 18 -pix_fmt yuv420p gource.mp4
```

De GitHub Actions workflow (`.github/workflows/gource.yml`) genereert de video automatisch bij elke release.

## Licentie

MIT
