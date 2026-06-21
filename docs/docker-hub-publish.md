# Docker Hub Publish

## Pre-requisitos

1. Cuenta en [hub.docker.com](https://hub.docker.com)
2. Repositorio creado: `juandelaf/raspal` (public)
3. Access Token en Docker Hub: Account Settings > Security > New Access Token (Read, Write, Delete)

## Configurar secrets en GitHub

1. Ir a: GitHub repo > Settings > Secrets and variables > Actions
2. Agregar `DOCKERHUB_USERNAME` = `juandelaf`
3. Agregar `DOCKERHUB_TOKEN` = el token generado en Docker Hub

## Publicar una version

```bash
git tag v0.5.2
git push origin v0.5.2
```

El workflow `.github/workflows/docker-publish.yml` hara el build multi-arch (amd64 + arm64) y pusheara automaticamente a Docker Hub.

## Verificar

```bash
docker run --rm juandelaf/raspal:latest raspal version
```
