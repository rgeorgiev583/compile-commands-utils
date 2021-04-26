#!/usr/bin/python

import argparse
import json
import os.path
import sys

from generate_header_compile_commands import (add_opts_to_argparser,
                                              generate_header_compile_commands)


def unescape_backslash_sequences(s: str) -> str:
    s = s.replace('\\:', ':')
    s = s.replace('\\\\', '\\')
    return s


argparser = argparse.ArgumentParser(
    description='Merge several compilation databases together, possibly substituting paths or adding entries for standalone headers.')
add_opts_to_argparser(argparser, True)
argparser.add_argument('-S', '--subst-path', nargs='*', metavar='SRC_PATH:DST_PATH',
                       help='substitute SRC_PATH with DST_PATH in compilation database entries')
argparser.add_argument(
    'compile_commands_file', nargs='+', default=os.path.curdir, help='path to `compile_commands.json` file to merge')
args = argparser.parse_args()

compile_commands = []
for compile_commands_file in args.compile_commands_file:
    with open(compile_commands_file, 'r') as compile_commands_file:
        compile_commands += json.load(compile_commands_file)

if args.subst_path:
    for subst_path in args.subst_path:
        (src_path, dst_path) = subst_path.split(':')
        src_path = unescape_backslash_sequences(src_path)
        dst_path = unescape_backslash_sequences(dst_path)
        for entry in compile_commands:
            for key in entry:
                entry[key] = entry[key].replace(src_path, dst_path)

if args.base_src_file:
    compile_commands_dict = {}
    for entry in compile_commands:
        compile_commands_dict[entry['file']] = entry
    for entry in generate_header_compile_commands(args, compile_commands_dict):
        compile_commands_dict[entry['file']] = entry
    compile_commands = list(compile_commands_dict.values())

json.dump(compile_commands, sys.stdout)
