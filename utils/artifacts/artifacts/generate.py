#!/usr/bin/python
"""
Generate the OPNFV HTML Dir site from a Google Storage bucket
"""
import sys
import os
import ConfigParser
import pkg_resources

from jinja2 import Environment, PackageLoader

from google.cloud import storage


FILES_SENTINAL = 'OPNFV_FILES_20171106'


def make_dir(directory):
    """Create a directory if it doesn't already exist"""
    if not os.path.exists(directory):
        os.makedirs(directory)


def bucket_prefixes(bucket):
    """Generate a set of prefixes to the delimieter used by the
    bucket"""
    iterator = bucket.list_blobs(delimiter='/')
    prefixes = set()
    for page in iterator.pages:
        prefixes.update(page.prefixes)
    return prefixes


def split_path(full_path):
    """Split a path and return the first part, and the rest of the
    path"""
    path = full_path.split('/')
    return (path[0], '/'.join(path[1:]))


def directory_tree(blobs):
    """Build a nested dict from a list, with the last element being the
    file

      foo/bar/baz.zip
      foo/bar/biz.zip

    becomes:

      {'foo':{'bar': {FILES_SENTINAL: [baz.zip, biz.zip]}}}
    """
    tree = dict()
    for blob in blobs:
        name_list = blob.name.split('/')[1:]
        prev = tree
        for i, key in enumerate(name_list):
            # When we get to the last element in the list, it should
            # point to the list of files found under that directory
            if i == len(name_list)-1:
                if FILES_SENTINAL not in prev:
                    prev[FILES_SENTINAL] = [blob]
                else:
                    prev[FILES_SENTINAL].append(blob)
            else:
                if key not in prev:
                    prev[key] = dict()
                prev = prev[key]
    return tree


def render_dir(template, directory, subdirs, blobs):
    """Render a directory tree from a collection of Google Storage
    blobs"""
    files = []
    for blob in blobs:
        if directory in blob.name:
            name = blob.name.split(directory)[1].lstrip('/')
        else:
            name = blob.name
        url_path = blob.public_url.split(blob.bucket.name)[1].lstrip('/').replace("%2F", "/")
        files.append(dict(
            blob=blob,
            name=name,
            url_path=url_path))
    directory = directory.rstrip('/')
    if '/' in directory:
        header = " > ".join(directory.split('/'))
    else:
        header = directory
    html = template.render(header=header, directories=subdirs, files=files)
    make_dir("output/{}".format(directory))
    with open("output/{}/index.html".format(directory), "wb") as newfile:
        newfile.write(html)


def render_tree(dirtree, template, parent):
    """Render directory tree templates"""
    if isinstance(dirtree, dict):
        keys = sorted(dirtree.keys())
        files = []
        if FILES_SENTINAL in keys:
            files = dirtree[FILES_SENTINAL]
            keys.remove(FILES_SENTINAL)
        print "Rendering %s files..." % parent
        sys.stdout.flush()
        render_dir(template, parent, keys, files)
        for key in keys:
            if parent.endswith('/'):
                parent = parent.rstrip('/')
            parent_str = "{}/{}".format(parent, key)
            render_tree(dirtree[key], template, parent=parent_str)


def main():
    """Main"""
    config = ConfigParser.ConfigParser()
    config.readfp(pkg_resources.resource_stream(__name__, "defaults.cfg"))
    config.read([os.path.expanduser('~/artifacts.cfg'), 'artifacts.cfg'])

    bucket_name = config.get('google-storage', 'bucket')
    prefixes = config.get('google-storage', 'prefixes')

    if prefixes:
        prefixes = prefixes.split(',')
    exclude_prefixes = config.get('google-storage', 'exclude_prefixes')
    if exclude_prefixes:
        exclude_prefixes = exclude_prefixes.split(',')

    # Create Jinja2 Environment
    env = Environment(
        loader=PackageLoader('artifacts', 'templates')
    )
    template = env.get_template('index.j2')

    client = storage.Client()
    bucket = client.get_bucket(bucket_name)

    # If no explicity prefixes are set, find all prefixes, and remove
    # those that should be excluded (if they exist)
    if not prefixes:
        prefixes = bucket_prefixes(bucket)
    if exclude_prefixes:
        for eprefix in exclude_prefixes:
            if eprefix in prefixes:
                prefixes.remove(eprefix)

    generate_site(bucket, prefixes, template)

def generate_site(bucket, prefixes, template):
    """Generate the HTML dir site from a Google Storage bucket"""
    make_dir("output")

    directories = []

    for prefix in prefixes:
        directory = prefix.strip('/')
        directories.append(directory)

        blobs = bucket.list_blobs(prefix=prefix)

        tree = directory_tree(blobs)

        render_tree(tree, template, prefix)

    rendered_template = template.render(directories=sorted(directories))
    with open("output/index.html", "wb") as newfile:
        newfile.write(rendered_template)


if __name__ == "__main__":
    main()
