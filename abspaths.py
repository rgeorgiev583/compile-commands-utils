#!/usr/bin/python3

import os.path
import json
import argparse
import sys


def make_include_paths_in_compile_commands_abs(path: str):
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
    argparser.add_argument('-c', dest='source_file')
    for cmd_obj in compile_commands:
        cmd_obj['file'] = os.path.normpath(
            os.path.join(cmd_obj['directory'], cmd_obj['file']))
        (parsed_args, remaining_args) = argparser.parse_known_args(
            cmd_obj['command'].split())
        for include_path in parsed_args.include_paths:
            remaining_args = [
                '-I', os.path.normpath(os.path.join(cmd_obj['directory'], include_path))] + remaining_args
        remaining_args += ['-c', os.path.normpath(
            os.path.join(cmd_obj['directory'], parsed_args.source_file))]
        cmd_obj['command'] = ' '.join(remaining_args)
    with open(compile_commands_path, 'w') as compile_commands_file:
        json.dump(compile_commands, compile_commands_file)


if len(sys.argv) == 1:
    make_include_paths_in_compile_commands_abs(os.path.curdir)
else:
    for path in sys.argv[1:]:
        make_include_paths_in_compile_commands_abs(path)
