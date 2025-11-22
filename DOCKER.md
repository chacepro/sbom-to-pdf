# Docker Setup Guide

This guide explains how to run the SBOM Flask application using Docker.

## Prerequisites

- Docker installed on your system
- Docker Compose (optional, for easier management)

## Building and Running

### Option 1: Using Docker Compose (Recommended)

```bash
# Build and start the container
docker-compose up --build

# Run in detached mode (background)
docker-compose up -d --build

# View logs
docker-compose logs -f

# Stop the container
docker-compose down
```

The application will be available at `http://localhost:5000`

### Option 2: Using Docker directly

```bash
# Build the image
docker build -t sbom-flask:latest .

# Run the container
docker run -d -p 5000:5000 --name sbom-flask-app sbom-flask:latest

# View logs
docker logs -f sbom-flask-app

# Stop the container
docker stop sbom-flask-app

# Remove the container
docker rm sbom-flask-app
```

## Environment Variables

You can customize the application behavior using environment variables:

- `FLASK_DEBUG`: Set to `true` to enable debug mode (default: `false`)
- `FLASK_HOST`: Host to bind to (default: `0.0.0.0`)
- `FLASK_PORT`: Port to listen on (default: `5000`)

Example with custom port:

```bash
docker run -d -p 8080:8080 -e FLASK_PORT=8080 --name sbom-flask-app sbom-flask:latest
```

## Health Check

The container includes a health check that verifies the application is running. You can check the health status:

```bash
docker ps
# Look for the "STATUS" column showing "healthy"
```

## Troubleshooting

### Container won't start

Check the logs:

```bash
docker logs sbom-flask-app
```

### Port already in use

Change the port mapping:

```bash
docker run -d -p 8080:5000 --name sbom-flask-app sbom-flask:latest
```

### Rebuild after code changes

```bash
docker-compose build --no-cache
docker-compose up -d
```
