#!/usr/bin/python

import argparse
import json
import os.path
import sys
from typing import Optional

BUILD_DIR = os.path.join(os.path.curdir, 'build')
COMPILEDB_PATH = os.path.join(os.path.curdir, 'compile_commands.json')
HEADER_EXTS = ['.h', '.hpp', '.hxx', '.hh', '.h++', '.hp']
IMPL_EXTS = ['.c', '.cpp', '.cxx', '.cc', '.c++', '.C']

argparser = argparse.ArgumentParser(
    description='Generate a compilation database containing entries for standalone C/C++ headers (i.e. headers without a corresponding implementation file) based on an entry from a `compile_commands.json` file.')
argparser.add_argument('-b', '--build-dir', metavar='PATH', default=BUILD_DIR,
                       help='use a custom build directory instead of `$PWD/build`')
argparser.add_argument('-c', '--compile-commands-file', metavar='PATH', default=COMPILEDB_PATH,
                       help='use a custom reference `compile_commands.json` file instead of `$PWD/compile_commands.json`')
argparser.add_argument('-i', '--generate-non-standalone-entries', action='store_true',
                       help='generate entries for non-standalone header files as well')
argparser.add_argument('-r', '--use-relative-paths', action='store_true',
                       help='use relative paths instead of absolute ones')
argparser.add_argument(
    'base_src_file', help='source file whose build command line to reuse for header entries')
argparser.add_argument(
    'src_dir', nargs='*', default=os.path.curdir, help='source directories to scan for header files')
args = argparser.parse_args()

if not args.use_relative_paths:
    args.build_dir = os.path.abspath(args.build_dir)

with open(args.compile_commands_file, 'r') as compile_commands_file:
    compile_commands = json.load(compile_commands_file)


def get_cmdline(filename: str) -> Optional[str]:
    for entry in compile_commands:
        if entry['file'] == filename:
            return entry['command']
    return None


fallback_cmdline = get_cmdline(args.base_src_file)
compile_commands_headers = []

for src_dir in args.src_dir:
    for dirpath, _, filenames in os.walk(src_dir):
        for filename in filenames:
            filepath = os.path.join(dirpath, filename)
            (filepath_noext, filepath_ext) = os.path.splitext(filepath)
            if filepath_ext in HEADER_EXTS:
                cmdline = None
                for impl_ext in IMPL_EXTS:
                    impl_filepath = filepath_noext + impl_ext
                    if os.path.exists(impl_filepath):
                        if args.generate_non_standalone_entries:
                            cmdline = get_cmdline(impl_filepath)
                        else:
                            cmdline = ""  # use a dummy value which is different from "None" to avoid fetching the cmdline for the impl file
                        if cmdline is not None:
                            break
                if cmdline is None:
                    cmdline = fallback_cmdline
                elif not args.generate_non_standalone_entries:
                    break
                if not args.use_relative_paths:
                    impl_filepath = os.path.abspath(impl_filepath)
                    filepath = os.path.abspath(filepath)
                cmdline = cmdline.replace(impl_filepath, filepath)
                entry = {"directory": args.build_dir,
                         "command": cmdline, "file": filepath}
                compile_commands_headers.append(entry)

json.dump(compile_commands_headers, sys.stdout)
