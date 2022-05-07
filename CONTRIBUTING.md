# Contribuir en el proyecto

A continuacion se listaran las herramientas necesarias para contribuir con el
desarrollo del proyecto.

## Herramientas necesarias

* [Docker](https://docs.docker.com/engine/install/ubuntu/)
* [Docker-Compose](https://docs.docker.com/compose/install/)
* [Direnv](https://direnv.net/)

## Produccion

### Comandos
Para desplegar localmente la API en modo produccion debemos ejecutar el
siguiente comando. Es importante que se haya creado previamente la red de
Redmine.

```bash
docker-prod up -d
```

## Desarrollo

### Comandos
Para desplegar la API en modo desarrollo debemos ejecutar el siguiente comando.
Previamente deberia estar creada la red Docker que utilizara Redmine.

```bash
docker-dev up -d
```
