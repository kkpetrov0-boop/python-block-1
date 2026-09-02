import csv
import statistics
import sys
from collections import defaultdict
from collections import Counter
import argparse

def parse_cmd():
    parser = argparse.ArgumentParser(prog="sensor-stats")
    parser.add_argument("file", help="file for log parsing")
    args = parser.parse_args()
    return args

def parse_csv(filename: str) -> tuple[defaultdict, Counter]:
    empty_val_flag = False
    errors = Counter()
    groups = defaultdict(list)
    with open(filename, newline="") as file:
        reader = csv.DictReader(file, delimiter=";")
        for line in reader:
            #print(line)
            if None in line or line["value"] is None:
                errors["fields_num_error"] += 1
                continue
            for k, v in line.items():
                #print(line[k])
                if not line[k]:
                    empty_val_flag = True
                    break
            if empty_val_flag:
                errors["empty_val_error"] += 1
                empty_val_flag = False
                continue
            try:
                float(line["value"])
                float(line["timestamp"])
                int(line["sensor_id"]) 
            except ValueError:
                errors["not_a_num_error"] += 1 
                continue        
                #groups[k].append(v)
            
            line["sensor_id"] = int(line["sensor_id"])    
            groups[line["sensor_id"]].append({"timestamp": line["timestamp"], "value": line["value"]})
        
        #print(groups)  
        return groups, errors

def count_stat(groups: dict):
    result = list(dict())
        
    for i in groups.keys():
        values = list()
        for y in groups[i]:
            y["timestamp"] = float(y["timestamp"])
            y["value"] = float(y["value"])
            values.append(y["value"])
        groups[i] = sorted(groups[i], key=lambda x: x["timestamp"])
        if (len(groups[i])) < 2:
            row = { "sensor_id": i,
                    "count": None,
                    "min": None, 
                    "max": None,
                    "mean": None,
                    "median": None,
                    "stdev": None}
            result.append(row)
            continue
        row = { "sensor_id": i,
                "count": len(groups[i]),
                "min": min(values), 
                "max": max(values),
                "mean": statistics.mean(values),
                "median": statistics.median(values),
                "stdev": statistics.stdev(values)}
        result.append(row)
    return result

def main():
    args = parse_cmd()
    groups, errors = parse_csv(args.file)

    groups = dict(sorted(groups.items()))
    result = count_stat(groups)
    for row in result:
        if any(val is None for val in row.values()):
            print(f"sensor_id = {row["sensor_id"]}  " + "-" * 77)
            continue
        print(f"sensor_id = {row["sensor_id"]}\tmin = {row["min"]:.3f}\tmax = {row["max"]:.3f}\tmean = {row["mean"]:.3f}\tmedian = {row["median"]:.3f}\tstdev = {row["stdev"]:.3f}")
    print(errors, file=sys.stderr)
    sys.exit(0)
        



if __name__ == "__main__":
    main()