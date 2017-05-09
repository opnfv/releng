#!/bin/bash
set +x
set -o errexit
for lab_configs in $(find labs/ -name 'pod.yaml'); do
        while IFS= read -r jinja_templates; do
          echo "./utils/generate_config.py -y $lab_configs -j $jinja_templates"
          ./utils/generate_config.py -y $lab_configs -j $jinja_templates
        done < <(find installers/ -name '*.j2')
done
