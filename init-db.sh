#!/bin/bash
set -e

psql -v ON_ERROR_STOP=1 --username "$POSTGRES_USER" --dbname "$POSTGRES_DB" <<-EOSQL
    CREATE USER vipul WITH PASSWORD '@Support4#';
    ALTER USER vipul WITH SUPERUSER;
    GRANT ALL PRIVILEGES ON DATABASE cheque_parser TO vipul;
EOSQL