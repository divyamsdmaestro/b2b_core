# Deployment Steps

1. Run the `deploy.sh` script located in `docker/deployment/scripts/`.
   1. If you cannot run the `deploy.sh` script because of Permission Denied.
      1. `ls -l docker/deployment/scripts/`
      2. `chmod +x docker/deployment/scripts/*.sh`
      3. Then run `sudo bash docker/deployment/scripts/deploy.sh`.
2. Now the necessary services will be running and the application can be accessed using `0.0.0.0:8000`.
3. Use nginx to proxy pass the necessary requests.
4. Just modify the necessary variables in `docker/deployment/conf/nginx-ssl.conf`.
5. Use `scripts/deployment/init-nginx-ssl.sh` to setup nginx.
