#!/usr/bin/python

import argparse
import json
import os.path
import sys
from typing import Dict, List, Optional

CompileCommandsEntry = dict[str, str]
CompileCommandsDict = dict[str, CompileCommandsEntry]

HEADER_EXTS = ['.h', '.hpp', '.hxx', '.hh', '.h++', '.hp']
IMPL_EXTS = ['.c', '.cpp', '.cxx', '.cc', '.c++', '.C']
DEFAULT_BUILD_DIR = os.path.join(os.path.curdir, 'build')
DEFAULT_COMPILE_COMMANDS_PATH = os.path.join(
    os.path.curdir, 'compile_commands.json')


def read_compile_commands_into_dict(compile_commands_path: str, compile_commands_dict: CompileCommandsDict):
    with open(compile_commands_path, 'r') as compile_commands_file:
        compile_commands = json.load(compile_commands_file)

    for entry in compile_commands:
        compile_commands_dict[entry['file']] = entry


def generate_header_compile_commands(args: argparse.Namespace, compile_commands_dict: CompileCommandsDict) -> List[CompileCommandsEntry]:
    if not args.use_relative_paths:
        args.base_src_file = os.path.abspath(args.base_src_file)
        args.build_dir = os.path.abspath(args.build_dir)

    def get_command(filename: str) -> Optional[str]:
        if filename in compile_commands_dict:
            return compile_commands_dict[filename]['command']
        return None

    fallback_command = get_command(args.base_src_file)
    header_compile_commands = []

    for src_dir in args.src_dir:
        for dirpath, _, filenames in os.walk(src_dir):
            for filename in filenames:
                filepath = os.path.join(dirpath, filename)
                (filepath_noext, filepath_ext) = os.path.splitext(filepath)
                if filepath_ext in HEADER_EXTS:
                    command = None
                    for impl_ext in IMPL_EXTS:
                        impl_filepath = filepath_noext + impl_ext
                        if os.path.exists(impl_filepath):
                            if args.generate_non_standalone_entries:
                                command = get_command(impl_filepath)
                            else:
                                command = ""  # use a dummy value which is different from "None" to avoid fetching the cmdline for the impl file
                            if command is not None:
                                break
                    if command is None:
                        command = fallback_command
                        impl_filepath = args.base_src_file
                    elif not args.generate_non_standalone_entries:
                        break
                    if not args.use_relative_paths:
                        impl_filepath = os.path.abspath(impl_filepath)
                        filepath = os.path.abspath(filepath)
                    command = command.replace(impl_filepath, filepath)
                    entry = {"directory": args.build_dir,
                             "command": command, "file": filepath}
                    header_compile_commands.append(entry)

    return header_compile_commands


def add_opts_to_argparser(argparser: argparse.ArgumentParser, is_external_command_invocation: bool = False):
    argparser.add_argument('-b', '--build-dir', metavar='PATH', default=DEFAULT_BUILD_DIR,
                           help='use a custom build directory instead of `$PWD/build`')
    if not is_external_command_invocation:
        argparser.add_argument('-c', '--compile-commands-file', metavar='PATH', default=DEFAULT_COMPILE_COMMANDS_PATH,
                               help='use a custom reference `compile_commands.json` file instead of `$PWD/compile_commands.json`')
    argparser.add_argument('-i', '--generate-non-standalone-entries', action='store_true',
                           help='generate entries for non-standalone header files as well')
    argparser.add_argument('-r', '--use-relative-paths', action='store_true',
                           help='use relative paths instead of absolute ones')
    if is_external_command_invocation:
        argparser.add_argument('-B',
                               '--base-src-file', metavar='PATH', help='source file whose build command line to reuse for header entries')
        argparser.add_argument('-s',
                               '--src-dir', nargs='*', default=os.path.curdir, help='source directories to scan for header files')


if __name__ == '__main__':
    argparser = argparse.ArgumentParser(
        description='Generate a compilation database on stdout containing entries for standalone C/C++ headers (i.e. headers without a corresponding implementation file) based on an entry from an existing compilation database (i.e. a `compile_commands.json` file).')
    add_opts_to_argparser(argparser)
    argparser.add_argument(
        'base_src_file', help='source file whose build command line to reuse for header entries')
    argparser.add_argument(
        'src_dir', nargs='*', default=os.path.curdir, help='source directories to scan for header files')
    args = argparser.parse_args()

    compile_commands_dict = {}
    read_compile_commands_into_dict(
        args.compile_commands_file, compile_commands_dict)
    json.dump(generate_header_compile_commands(
        args, compile_commands_dict), sys.stdout)
