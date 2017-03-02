from argparse import ArgumentParser

from spotrun.config_schema import ConfigSchema
from spotrun.task import Task

import json
import os


def main():
    parser = ArgumentParser()

    parser.add_argument('task_manifest')

    args = parser.parse_args()

    if not os.path.isfile(args.task_manifest):
        print("Error: File '{}' does not exist".format(args.task_manifest))
        return

    config, errors = load_config_file(args.task_manifest)

    if errors:
        print("Error: Invalid Schema:")
        for k, v in errors.items():
            print('"{k}": {v}'.format(k=k, v=v[0]))
        return

    t = Task(config)

    t.setup()
    t.execute()
    t.teardown()


def load_config_file(filepath):

    with open(filepath, 'r') as infile:
        config, errors = ConfigSchema().load(json.load(infile))

    return config, errors


if __name__ == '__main__':
    main()
