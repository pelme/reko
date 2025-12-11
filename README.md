# reko

A webapp that lets you buy food directly from your local farmers. This project
is in an early and experimental stage.

## Deployment

A reference deployment is available at https://handlareko.se/demo.

### Important locations
 - Docker compose configuration: `/etc/reko`.
 - Postgres data files: `/var/lib/postgresql/`.

### Deploy a new version.

Run the `bin/deploy` script to upgrade the handlareko VM to the latest version.

### Docker Compose service management

#### Stop all services:
```
docker compose down
```

#### Start all services (and detach from terminal):
```
docker compose up -d
```

#### Enter the Python environment:

```
docker exec -it reko-app-1 bash
```

You may then interact with Python/Django:
```
django-admin shell
django-admin dbshell
dev-db-generate --create-superuser
```


### Reset the production database
```
cd /etc/reko
docker compose down
mv /var/lib/postgresql/reko /var/lib/postgresql/reko-old-$(date -I)
docker compose up -d
docker exec -it reko-app-1 bash
dev-db-generate --create-superuser
```
