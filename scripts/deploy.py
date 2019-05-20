#!/bin/env python3
import os
import os.path
import argparse
from jinja2 import Environment, BaseLoader
abspath = os.path.abspath
join = os.path.join

GENERATED_HEADER = '# # # # GENERATED FILE -- DO NOT MODIFY # # # #\n'


def main(version, repourl):
    SCRIPT_DIR = os.path.dirname(__file__)
    ROOT_DIR = abspath(join(SCRIPT_DIR, ".."))
    SETUP_IN = abspath(join(ROOT_DIR, "setup.py.in"))
    SETUP_OUT = abspath(join(ROOT_DIR, "setup.py"))
    VERSION_OUT = abspath(join(ROOT_DIR, "aat", "_version.py"))

    DOCS_CONF_IN = abspath(join(ROOT_DIR, "docs", "conf.py.in"))
    DOCS_CONF_OUT = abspath(join(ROOT_DIR, "docs", "conf.py"))

    with open(SETUP_IN, 'r') as fp:
        setup_in = fp.read()

    with open(DOCS_CONF_IN, 'r') as fp:
        docs_conf_in = fp.read()

    # write out setup.py
    with open(SETUP_OUT, "w") as fp:
        template = Environment(loader=BaseLoader).from_string(setup_in)
        fp.write(GENERATED_HEADER)
        fp.write(template.render(
            VERSION=version,
            REPO_URL=repourl
            ) + '\n')

    # write out _version.py
    with open(VERSION_OUT, "w") as fp:
        template = Environment(loader=BaseLoader).from_string("VERSION = 'v{{VERSION}}'")
        fp.write(GENERATED_HEADER)
        fp.write(template.render(
            VERSION=version
            ) + '\n')

    # write out docs/conf.py
    with open(DOCS_CONF_OUT, "w") as fp:
        template = Environment(loader=BaseLoader).from_string(docs_conf_in)
        fp.write(GENERATED_HEADER)
        fp.write(template.render(
            VERSION=version
            ) + '\n')

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Process some integers.')
    requiredNamed = parser.add_argument_group('required named arguments')
    requiredNamed.add_argument('--version', type=str, required=True, help='Version number to generate (format Major.Minor.Micro)')
    requiredNamed.add_argument('--repourl', type=str, required=True, help='Github repository')
    args = parser.parse_args()
    main(args.version, args.repourl)
