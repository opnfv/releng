#!/bin/bash
FILE=/etc/opnfv_testapi/config.ini


if [ "$mongodb_url" != "" ]; then
    sudo crudini --set --existing $FILE mongo url $mongodb_url
fi

if [ "$swagger_url" != "" ]; then
    sudo crudini --set --existing $FILE swagger base_url $swagger_url
fi

if [ "$api_port" != "" ];then
    sudo crudini --set --existing $FILE api port $api_port
fi

