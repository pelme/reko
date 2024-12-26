#! /user/bin/env bash
set -e

psql -v ON_ERROR_STOP=1 --username "$POSTGRES_USER" --dbname "$POSTGRES_DB" <<-EOSQL
	CREATE USER reko WITH PASSWORD '$DB_USER_PASSWORD';
	CREATE DATABASE reko OWNER reko;
	GRANT ALL PRIVILEGES ON DATABASE reko TO reko;
EOSQL
