#!/bin/bash

export PATH=$PATH:/usr/local/bin/

# clone releng repository
echo "Cloning releng repository..."
[ -d releng ] && rm -rf releng
git clone https://gerrit.opnfv.org/gerrit/releng $WORKSPACE/releng/ &> /dev/null
#this is where we import the siging key
if [ -f $WORKSPACE/releng/utils/gpg_import_key.sh ]; then 
  source $WORKSPACE/releng/utils/gpg_import_key.sh
fi

artifact="foo"
echo foo > foo

testsign () {
  echo "Signing artifact: ${artifact}"
  gpg2 -vvv --batch \
    --default-key opnfv-helpdesk@rt.linuxfoundation.org  \
    --passphrase besteffort \
    --detach-sig $artifact
done
}

testsign

