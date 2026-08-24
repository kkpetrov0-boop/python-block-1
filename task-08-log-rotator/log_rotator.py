import argparse
from dataclasses import dataclass
import gzip
import shutil
import os
import time
from datetime import datetime, timezone
from pathlib import Path
from collections import defaultdict

@dataclass
class Action:
    kind: str
    source: Path
    destination: Path | None = None



def cmd_parse() -> argparse.Namespace:
    parser = argparse.ArgumentParser(prog="log_rotator")
    parser.add_argument("--dir", help="Takes this address for log search")
    parser.add_argument("--size-mb", help="Takes only logs, that exceeds the size", type=int)
    parser.add_argument("--keep", help="Keep only n last logs for each name", nargs="?", default=5, type=int)
    parser.add_argument("--dry-run", help="Show the list of steps, but do not change any file", action="store_true")
    args = parser.parse_args()
    return args

def create_plan(location, keep, max_size):
    paths = []
    plan = []
    archieve_list = defaultdict(list)
    date = datetime.now(timezone.utc)
    date = date.strftime("%Y%m%d%H%M%S")

    paths = list(Path(location).rglob("*.log"))

    for i in range(len(paths)):
        file_name = paths[i].name
        file_path = paths[i].parent
        size = os.stat(paths[i]).st_size
        if max_size*1024*1024 > size:
            continue
        new_path = f"{file_name}.{date}.gz"
        action = Action("archive", paths[i], file_path / new_path)
        plan.append(action)
        archieve_list[file_path / file_name].append(Path(file_path / new_path))
    
    old_log_paths = list(Path(location).rglob("*.log.*.gz"))
    for i in range(len(old_log_paths)):
        file_name = old_log_paths[i].name
        origin_name = file_name.rsplit(".", maxsplit=2)[0]
        file_path = old_log_paths[i].parent
        archieve_list[file_path / origin_name].append(old_log_paths[i]) 

    for key, value in archieve_list.items():
        value.sort()
        for file in value[:-keep]:
            delete = Action("delete", file)
            plan.append(delete)
    return plan

def exec_plan(plan, location, copy_func=shutil.copyfileobj):
    tmp_garbage = list(Path(location).rglob("*.tmp"))
    for each_file in tmp_garbage:
        os.remove(each_file)
    for action in plan:
        if action.kind == "archive":
            tmp_file = action.destination.with_name(action.destination.name + ".tmp")
            with open(action.source, "rb") as src, gzip.open(tmp_file, "wb") as dst:
                copy_func(src, dst)
            os.replace(tmp_file, action.destination)
            os.remove(action.source)
        elif action.kind == "delete":
            os.remove(action.source)
    
def main():
    args = cmd_parse()
    plan = create_plan(args.dir, args.keep, args.size_mb) 
    if args.dry_run:
        for action in plan:
            if action.kind == "archive":
                print(f"Archive {action.source} to {action.destination}")
            elif action.kind == "delete":
                print(f"Delete {action.source}")
    else:
        exec_plan(plan, args.dir)
        
if __name__ == "__main__":
    main()