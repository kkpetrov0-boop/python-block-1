from abc import ABC, abstractmethod
import argparse
from dataclasses import dataclass
from enum import StrEnum
import signal
import sys
import os
from pathlib import Path
import time
import json
import re
from collections import Counter

running = True

def interrupt_handler(signum, frame):
    global running
    running = False

def parse_cmd():
    parser = argparse.ArgumentParser(prog="logtail")
    parser.add_argument("file",help= "filepath to observed file")
    parser.add_argument("--group-by", help="Choose the group level", required=True)
    parser.add_argument("--interval", help="Specify print interval", type=int, default=10)
    parser.add_argument("--format", help="Choose json or table format", required=True)
    parser.add_argument("--pattern", help="Regex pattern for search and group", required=True)
    args = parser.parse_args()
    return args


@dataclass
class FileState():
    file_path: Path
    file_id: int
    endpoint: int

class_dict = {}

class FormatEnum(StrEnum):
    JSON = "json"
    TABLE = "table"

class FormatClass(ABC):
    def __init_subclass__(cls):
        global class_dict
        class_name = cls.class_name
        class_dict[class_name.value] = cls

    @abstractmethod
    def format_out(self, payload: Counter):
        ...

@dataclass
class JsonFormat(FormatClass):
    class_name = FormatEnum.JSON
    @staticmethod
    def format_out(payload: Counter):
        m = json.dumps(dict(payload))
        return m


@dataclass
class TableFormat(FormatClass):
    class_name = FormatEnum.TABLE
    @staticmethod
    def format_out(payload: Counter):
        lines = ""
        for k, v in dict(payload).items():
            lines += str(k)+": " + str(v) + "\n"
        return lines


def return_global():
    return running


def observe_file(file, formatter, p, group_by, interval, sleep=time.sleep, time_counter=time.perf_counter, sleep_delay=1, running_cond=return_global):
    file_state = FileState(file_path=Path(file), file_id=0, endpoint=0)
    c = Counter()
    start = Interval(time_counter, interval)
    
    while running_cond():
        try:
            with open(file_state.file_path, "r") as f: 
                
                stats = os.stat(file_state.file_path)
                if check_rotation(stats, file_state):
                    file_state.endpoint = 0
                f.seek(file_state.endpoint)

                for line in read_file(f):
                    group_name = parse_string(line, p, group_by)
                    c.update({group_name: 1})

                file_state.endpoint = f.tell()
                file_state.file_id = os.stat(file_state.file_path).st_ino

                if start.check_interval():
                    result = formatter.format_out(c)
                    print(result)
            
        except FileNotFoundError:
            print("File is missing, trying to find...", file=sys.stderr)
            sleep(sleep_delay)
            continue  
        sleep(sleep_delay)

    result = formatter.format_out(c)
    print(result)


def read_file(f):
    line = f.readline()
    while line != "":
        yield line
        line = f.readline()

def check_rotation(stats, file_state):
    if stats.st_size < file_state.endpoint or file_state.file_id != stats.st_ino:
        return True
    return False


class Interval():
    def __init__(self, time_counter, interval):
        self.start = time_counter()
        self.time_counter = time_counter
        self.interval = interval

    def check_interval(self):
        if self.time_counter() - self.start > self.interval:
            self.start = self.time_counter()
            return True
        return False

    
def parse_string(line, p, group_name):
    m = p.search(line)
    if m:
        result = m.group(group_name)
    else:
        result = "missing"
    return result

def main():
    signal.signal(signal.SIGINT, interrupt_handler)
    signal.signal(signal.SIGTERM, interrupt_handler)

    args = parse_cmd()

    try:
        formatter = class_dict[args.format]
    except KeyError as e:
        print(f"Invalid format: {e}", file=sys.stderr)
        sys.exit(2)

    pattern = re.compile(args.pattern)
    if not Path(args.file).is_file():
        print(f"{args.file} is not a file", file=sys.stderr)
        sys.exit(2)
    if args.group_by in pattern.groupindex:
        observe_file(args.file, formatter, pattern, args.group_by, args.interval)
        sys.exit(0)
    else:
        print(f"Wrong group name, received: {args.group_by}, from pattern: {pattern.groupindex}", file=sys.stderr)
        sys.exit(2)


if __name__ == "__main__":
    main()