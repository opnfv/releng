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
      - base_url={{ vars.testapi_base_url }}
    ports:
      - "{{ vars.testapi_port }}:8000"
    links:
      - mongo
"""


def render_docker_compose(testapi_port, testapi_base_url):
    vars = {
        "testapi_port": testapi_port,
        "testapi_base_url": testapi_base_url,
    }

    yml = Environment().from_string(DOCKER_COMPOSE_TEMPLATE).render(vars=vars)

    with open(DOCKER_COMPOSE_FILE, 'w') as f:
        f.write(yml)
        f.close()


def main(args):
    render_docker_compose(args.testapi_port, args.testapi_base_url)
    os.system('docker-compose -f {} up -d'.format(DOCKER_COMPOSE_FILE))


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Backup MongoDBs')
    parser.add_argument('-tp', '--testapi-port',
                        type=int,
                        required=False,
                        default=8000,
                        help='testapi exposed port')
    parser.add_argument('-tl', '--testapi-base-url',
                        type=str,
                        required=True,
                        help='testapi exposed base-url')
    main(parser.parse_args())
