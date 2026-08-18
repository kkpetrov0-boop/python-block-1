from csv_parser import parse_csv
from csv_parser import count_stat
import math
import time

groups, errors = parse_csv("test_text_file.csv")
result = count_stat(groups)

assert len(result) == 4, f"Wrong number of ids {len(result)}"
assert errors == {'empty_val_error': 2, 'not_a_num_error': 3, 'fields_num_error': 2}, f"Wrong error numbers {errors}"
row  = next(r for r in result if r["sensor_id"] == 1)
assert row["count"] == 4, f"Wrong count result {result[0]["count"]}"
assert row["min"] == 10, f"Wrong mean result {result[0]["min"]}"
assert row["max"] == 25, f"Wrong mean result {result[0]["max"]}"
assert math.isclose(row["mean"], 16.75), f"Wrong mean result {result[0]["mean"]}"
assert math.isclose(row["median"], 16.0), f"Wrong mean result {result[0]["median"]}"
assert math.isclose(row["stdev"], 6.238322424070967), f"Wrong mean result {result[0]["stdev"]}"
assert result[3]["stdev"] is None, "Stdev is not 'None', while only one result is in place"

start = time.perf_counter()
groups, errors = parse_csv("text_file.csv")
result = count_stat(groups)
final_time = time.perf_counter() - start
assert final_time < 5.0, f"Working time is too long {final_time}"