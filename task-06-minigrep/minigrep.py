import argparse
import re
import sys
from pathlib import Path
from collections.abc import Iterable


def cmd_parse() -> argparse.Namespace:
    parser = argparse.ArgumentParser(prog="minigrep")
    parser.add_argument("-i", "--ignore", help="ignore the register", action="store_true")
    parser.add_argument("-v", "--inverse", help="inverse the search", action="store_true")
    parser.add_argument("-n", "--line-number", help="check specific line", action="store_true")
    parser.add_argument("-c", "--count", help="only amount", action="store_true")
    parser.add_argument("pattern", help="Pattern for search")
    parser.add_argument("file", help="Specify files, where the search will be", nargs="*")
    args = parser.parse_args()
    return args

def search_in_text(prog, lines: Iterable, invert) -> list:
    result = list()
    for index, line in enumerate(lines, start=1):
        msg = prog.search(line)
        if bool(msg) != invert:
            result.append((index, line))
    return result

def process(prog, name, stream, args, show_prefix) -> bool:
    matches = search_in_text(prog, stream, args.inverse)
    printed_line = ""
    if show_prefix:
        printed_line = f"{name}:"

    if args.count:
        print(f"{printed_line}{len(matches)}")
        return bool(matches)

    for num, line in matches:
        if args.line_number:
            new_printed_line = printed_line + f"{num}: "
        else:
            new_printed_line = printed_line
        print(f"{new_printed_line}{line.rstrip("\n")}")

    return bool(matches)

def main():
    args = cmd_parse()

    try:
        prog = re.compile(args.pattern, re.IGNORECASE if args.ignore else 0)
    except re.error as e:
        print(f"Invalid regular expression: {e.msg} at {e.pos}",file=sys.stderr)
        sys.exit(2)

    found_any = False
    had_error = False   

    files = []
    if args.file:
        for name in args.file:
            if "*" in name or "?" in name:
                p = Path(name)
                file_path = [str(f) for f in p.parent.glob(p.name)]
                files.extend(file_path)
                if not file_path:
                    print(f"Can not find a file: {p}", file=sys.stderr)
                    had_error = True
            else:
                files.append(name)
            
        for name in files:
            try:
                with Path(name).open() as stream:
                    found_any |= process(prog, name, stream, args, len(files) > 1)
            except OSError as e:
                print(f"minigrep: {name}: {e.strerror}", file=sys.stderr)
                had_error = True
    else:
        found_any |= process(prog, None, sys.stdin, args, False)
    if had_error:
        sys.exit(2)
    sys.exit(0 if found_any else 1)

if __name__ == "__main__":
    main()