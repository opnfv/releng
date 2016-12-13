import argparse
import os

from jinja2 import Environment, FileSystemLoader

env = Environment(loader=FileSystemLoader('./'))
docker_compose_yml = './docker-compose.yml'
docker_compose_template = './docker-compose.yml.template'


def render_docker_compose(port, swagger_url):
    vars = {
        "expose_port": port,
        "swagger_url": swagger_url,
    }
    template = env.get_template(docker_compose_template)
    yml = template.render(vars=vars)

    with open(docker_compose_yml, 'w') as f:
        f.write(yml)
        f.close()


def main(args):
    render_docker_compose(args.expose_port, args.swagger_url)
    os.system('docker-compose -f {} up -d'.format(docker_compose_yml))


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Backup MongoDBs')
    parser.add_argument('-p', '--expose-port',
                        type=int,
                        required=False,
                        default=8000,
                        help='testapi exposed port')
    parser.add_argument('-su', '--swagger-url',
                        type=str,
                        required=True,
                        help='testapi exposed swagger-url')
    main(parser.parse_args())
