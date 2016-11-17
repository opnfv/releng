#!/bin/bash

echo "--------------------------------------------------------"
echo "This is diasy4nfv virtual deploy job!"
echo "--------------------------------------------------------"

# start the deploy
cd $WORKSPACE
./ci/deploy/deploy.sh
