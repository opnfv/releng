import argparse
import os

from jinja2 import Environment

DOCKER_COMPOSE_FILE = './docker-compose.yml'
DOCKER_COMPOSE_TEMPLATE = """
version: '2'
services:
  mongo:
    image: mongo:3.2.1
    container_name: opnfv-mongo
  testapi:
    image: opnfv/testapi:latest
    container_name: opnfv-testapi
    environment:
      - mongodb_url=mongodb://mongo:27017/
      - base_url={{ vars.base_url }}
    ports:
      - "{{ vars.testapi_port }}:8000"
    links:
      - mongo
  reporting:
    image: opnfv/reporting:latest
    container_name: opnfv-reporting
    ports:
      - "{{ vars.reporting_port }}:8000"
"""


def render_docker_compose(testapi_port, reporting_port, base_url):
    vars = {
        "testapi_port": testapi_port,
        "reporting_port": reporting_port,
        "base_url": base_url,
    }
    yml = Environment().from_string(DOCKER_COMPOSE_TEMPLATE).render(vars=vars)
    with open(DOCKER_COMPOSE_FILE, 'w') as f:
        f.write(yml)
        f.close()


def main(args):
    render_docker_compose(args.testapi_port,
                          args.reporting_port,
                          args.base_url)
    os.system('docker-compose -f {} up -d'.format(DOCKER_COMPOSE_FILE))


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Backup MongoDBs')
    parser.add_argument('-tp', '--testapi-port',
                        type=int,
                        required=False,
                        default=8082,
                        help='testapi exposed port')
    parser.add_argument('-l', '--base-url',
                        type=str,
                        required=True,
                        help='testapi exposed base-url')
    parser.add_argument('-rp', '--reporting-port',
                        type=int,
                        required=False,
                        default=8084,
                        help='reporting exposed port')

    main(parser.parse_args())