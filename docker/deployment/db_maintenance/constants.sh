#!/usr/bin/env bash


BACKUP_DIR_PATH='/backups'
BACKUP_FILE_PREFIX='backup'

# db.yml -> services -> postgres | used in `./backup` & `./restore`
DOCKER_COMPOSE_DB_SERVICE_NAME='postgres'
