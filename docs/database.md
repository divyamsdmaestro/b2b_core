# Backup Database

Run the command: `docker-compose -f docker/deployment/db.yml run postgres backup`.


# Upload To S3

Run the command: `docker-compose -f docker/deployment/db.yml run postgres upload`.


# Download Backup File From S3

Run the command: `docker-compose -f docker/deployment/db.yml run postgres download <filename>`.


# Restore Database

Run the command: `docker-compose -f docker/deployment/db.yml run postgres restore <filename>`.


# Database Backup CRON

Make sure to set `docker-compose -f docker/deployment/db.yml run postgres backup && docker-compose -f docker/deployment/db.yml run postgres upload`
on your `crontab -e`, with necessary time period.
