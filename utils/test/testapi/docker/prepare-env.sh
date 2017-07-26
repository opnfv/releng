#!/bin/bash
FILE=/etc/opnfv_testapi/config.ini


if [ "$mongodb_url" != "" ]; then
    sudo crudini --set --existing $FILE mongo url $mongodb_url
fi

if [ "$base_url" != "" ]; then
    sudo crudini --set --existing $FILE api url $base_url/api/v1
    sudo crudini --set --existing $FILE ui url $base_url
    sudo echo "{\"testapiApiUrl\": \"$base_url/api/v1\"}" > \
        /usr/local/lib/python2.7/dist-packages/opnfv_testapi/static/testapi-ui/config.json
fi
