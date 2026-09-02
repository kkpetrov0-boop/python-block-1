from log_utilities.csv_parser import parse_csv
from log_utilities.csv_parser import count_stat
from text_file_maker import make_file
import math
import time
import pytest
import csv


@pytest.fixture
def build_huge_file(tmp_path, monkeypatch):
    monkeypatch.chdir(tmp_path)
    p = tmp_path / "text_file.csv"
    make_file(p)
    return p


@pytest.fixture
def build_file(tmp_path, monkeypatch):
    monkeypatch.chdir(tmp_path)
    p = tmp_path / "text_file.csv"
    lines = [
            ["timestamp","sensor_id","value"],
            [1,1,10],
            [11,1,15],
            [6,1,""],
            [1,"asdsad",12],
            [3,1,17],
            [5,1,25],
            [2,1,21,333312111],
            [1,2,10],
            [11,2,15],
            [6,2,20],
            [5,2,12],
            ["sadddd",2,17],
            [5,2,25],
            [2,2,""],
            [1,3,10],
            [11,3,15],
            [6,3,20],
            [5,3,12],
            [3,3,17],
            ["aaaa231",3,25],
            [2,3,21,233333],
            [5,4,25],
        ]
    with open(p.name, mode="w", newline="", encoding="utf-8") as file:
        csv_writer = csv.writer(file, delimiter=";")
        csv_writer.writerows(lines)
    return p

@pytest.mark.parametrize("id,count,min_val,max_val,mean,median,stdev",[
    (1, 4, 10, 25, 16.75, 16.0, 6.238322424070967),
    (2, 5, 10, 25, 16.4, 15.0, 6.107372593840988),
    (3, 5, 10, 20, 14.8, 15.0, 3.96232255123179)
])
def test_parse_and_stats(id, count, min_val, max_val, mean, median,stdev,tmp_path, monkeypatch, build_file):
    p = build_file
    groups, errors = parse_csv(p)
    result = count_stat(groups)
    row  = next(r for r in result if r["sensor_id"] == id)
    assert row["count"] == count
    assert row["min"] == min_val
    assert row["max"] == max_val
    assert math.isclose(row["mean"], mean)
    assert math.isclose(row["median"], median)
    assert math.isclose(row["stdev"], stdev)


def test_errors_stat(tmp_path, monkeypatch, build_file):
    p = build_file
    groups, errors = parse_csv(p)
    result = count_stat(groups)
    assert len(result) == 4
    assert errors == {'empty_val_error': 2, 'not_a_num_error': 3, 'fields_num_error': 2}
    assert next(r for r in result if r["sensor_id"] == 4)["stdev"] is None

@pytest.mark.slow
def test_time(tmp_path, monkeypatch, build_huge_file):
    p = build_huge_file
    start = time.perf_counter()
    groups, errors = parse_csv(p)
    result = count_stat(groups)
    final_time = time.perf_counter() - start
    assert final_time < 5.0, f"Working time is too long {final_time}"
