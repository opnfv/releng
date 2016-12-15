#!/usr/bin/env python

# All rights reserved. This program and the accompanying materials
# are made available under the terms of the Apache License, Version 2.0
# which accompanies this distribution, and is available at
# http://www.apache.org/licenses/LICENSE-2.0

import argparse
import requests
import json
import os


def main(args):

    # Merging two specs
    api_response = requests.get(args.api_declaration_url)
    api_response = json.loads(api_response.content)
    resource_response = requests.get(args.resource_listing_url)
    resource_response = json.loads(resource_response.content)
    resource_response['models'] = api_response['models']
    resource_response['apis'] = api_response['apis']

    # Storing the swagger specs
    with open('specs.json', 'w') as outfile:
        json.dump(resource_response, outfile)

    # Generating html page
    cmd = 'java -jar swagger-codegen-cli.jar generate \
        -i specs.json -l html2 -o %s' % (args.output_directory)
    os.system(cmd)

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Create \
                                      Swagger Spec documentation')
    parser.add_argument('-ru', '--resource-listing-url',
                        type=str,
                        required=False,
                        default='http://localhost:8000/swagger/spec.json',
                        help='Resource Listing Spec File')
    parser.add_argument('-au', '--api-declaration-url',
                        type=str,
                        required=False,
                        default='http://localhost:8000/swagger/spec',
                        help='API Declaration Spec File')
    parser.add_argument('-o', '--output-directory',
                        required=True,
                        default='./',
                        help='Output Directory where the \
                                file should be stored')
    main(parser.parse_args())
