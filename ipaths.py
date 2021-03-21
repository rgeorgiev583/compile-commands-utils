#!/usr/bin/python3

import os.path
import json
import argparse
import sys


def get_relpath_with_prefix(path: str, prefix: str, curdir: str) -> str:
    if os.path.isabs(path):
        return os.path.relpath(path, start=curdir)

    return os.path.normpath(os.path.join(prefix, path))


def get_include_paths_from_compile_commands(path: str):
    compile_commands_path = os.path.join(path, 'compile_commands.json')
    try:
        with open(compile_commands_path, 'r') as compile_commands_file:
            compile_commands = json.load(compile_commands_file)
    except OSError:
        print(format('error: file {} does not exist', compile_commands_path))
        return

    argparser = argparse.ArgumentParser()
    argparser.add_argument('-I', action='append',
                           default=[], dest='include_paths')
    for cmd_obj in compile_commands:
        if os.path.isabs(cmd_obj['directory']):
            dir_rel = os.path.relpath(cmd_obj['directory'], start=path)
        else:
            dir_rel = cmd_obj['directory']
        file_dir = os.path.dirname(cmd_obj['file'])
        print(get_relpath_with_prefix(file_dir, dir_rel, path))
        parsed_args = argparser.parse_known_args(cmd_obj['command'].split())
        for include_path in parsed_args[0].include_paths:
            print(get_relpath_with_prefix(include_path, dir_rel, path))


if len(sys.argv) == 1:
    get_include_paths_from_compile_commands(os.path.curdir)
else:
    for path in sys.argv[1:]:
        get_include_paths_from_compile_commands(path)
