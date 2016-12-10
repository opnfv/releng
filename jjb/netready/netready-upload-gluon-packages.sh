#!/bin/bash
set -o errexit
set -o nounset
set -o pipefail

echo "Uploading Gluon packages"
echo "--------------------------------------------------------"
echo

source $WORKSPACE/opnfv.properties

for artifact in $ARTIFACT_LIST; do
  echo "Uploading artifact: ${artifact}"
  gsutil cp $artifact gs://$GS_URL/$(basename $artifact) > gsutil.$(basename $artifact).log
  echo "Upload complete for ${artifact}"
done

gsutil cp $WORKSPACE/opnfv.properties gs://$GS_URL/opnfv-$OPNFV_ARTIFACT_VERSION.properties > gsutil.properties.log

echo "--------------------------------------------------------"
echo "Upload done!"

echo "Artifacts are not available as:"
for artifact in $ARTIFACT_LIST; do
  echo "http://$GS_URL/$(basename $artifact)"
done
