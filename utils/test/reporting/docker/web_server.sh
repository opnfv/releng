#!/bin/bash
cp -r display /usr/share/nginx/html


# nginx config
cp /home/opnfv/releng/utils/test/reporting/docker/nginx.conf /etc/nginx/conf.d/
echo "daemon off;" >> /etc/nginx/nginx.conf

# supervisor config
cp /home/opnfv/releng/utils/test/reporting/docker/supervisor.conf /etc/supervisor/conf.d/

ln -s /usr/bin/nodejs /usr/bin/node

# Manage Angular front end
cd pages && /bin/bash angular.sh

