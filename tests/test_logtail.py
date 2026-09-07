from pathlib import Path

import pytest
import re
from collections import Counter
import json
import os
import sys
from src.log_utilities.logtail import observe_file, parse_string, JsonFormat, TableFormat, check_rotation, FileState, Interval, read_file, main

@pytest.mark.parametrize("line,pattern,group_name,result",[
    ("ERROR module2 asda", r"(?P<level>\w+)\s+(?P<module>\S+)", "level", "ERROR"),
    ("asda", r"(?P<level>\w+)\s+(?P<module>\S+)", "level", "missing"),
    ("ERROR", r"(?P<level>\w+)\s+(?P<module>\S+)", "module", "missing")
])
def test_parse_string(line, pattern, group_name, result):
    pattern = re.compile(pattern)
    res = parse_string(line, pattern, group_name)
    assert result == res

def test_json_formatter():
    c = Counter({"ERROR": 1, "INFO": 4})
    res = json.loads(JsonFormat().format_out(c))
    assert res == c

def test_table_formatter(): 
    c = Counter({"ERROR": 1, "INFO": 4})
    res = TableFormat().format_out(c)
    assert res == "ERROR: 1\nINFO: 4\n"  


@pytest.fixture
def build_file(tmp_path):
    p = tmp_path / "app.log"
    lines = """ERROR module2 asda
ERROR module3 dsad
INFO module1 ddddddd
DEBUG module2  asdad
INFO module1 tweq
ERROR module2 sadzxc
ERROR module1 sss
WARNING module4
!;dsa?F//FSAD"""
    p.write_text(lines, encoding="utf-8")
    return p

@pytest.fixture
def build_empty_file(tmp_path):
    p = tmp_path / "app_empty.log"
    lines = ""
    p.write_text(lines, encoding="utf-8")
    return p

@pytest.mark.parametrize("path,file_id,point,result", [
    ("app.log", "app.log", 0, False),
    ("app_empty.log", "app_empty.log", 50, True),
    ("app.log", "app_empty.log", 0, True),
    ("app.log", "app_empty.log", 50, True),
])
def test_check_rotation(path,file_id,point, result,build_file, build_empty_file, tmp_path, monkeypatch):
    monkeypatch.chdir(tmp_path)
    file_state = FileState(path, os.stat(file_id).st_ino, point)
    stats = os.stat(file_state.file_path)
    assert check_rotation(stats, file_state) == result



def test_read(build_file, tmp_path, monkeypatch):
    monkeypatch.chdir(tmp_path)
    lines = ["ERROR module2 asda\n",
        "ERROR module3 dsad\n",
        "INFO module1 ddddddd\n",
        "DEBUG module2  asdad\n",
        "INFO module1 tweq\n",
        "ERROR module2 sadzxc\n",
        "ERROR module1 sss\n",
        "WARNING module4\n",
        "!;dsa?F//FSAD"]

    with open("app.log", "r") as f:
        for index, val in enumerate(read_file(f)):
            assert val == lines[index]
        assert f.readline() == ""

def get_next_number():
    numbers = [0, 5, 5, 6, 10, 10]
    num = (i for i in numbers)
    def gen_number():
        return next(num)
    return gen_number

def test_interval_class():
    interval_counter = Interval(get_next_number(), 2)

    assert interval_counter.check_interval() == True
    assert interval_counter.check_interval() == False
    assert interval_counter.check_interval() == True


def get_next_number_of():
    numbers = [0,1,2,3,4,5,6,7,8, 10, 20, 30]
    num = (i for i in numbers)
    def gen_number():
        return next(num)
    return gen_number

def get_running_cond():
    conds = [True, True, True, False]
    cond = (i for i in conds)
    def get_cond():
        return next(cond)
    return get_cond

def return_none(num):
    return None


@pytest.mark.parametrize("file_name,file_format,pattern_p,group,result",[
    ("app.log", JsonFormat, r"(?P<level>\w+)\s+(?P<module>\S+)", "level", {"ERROR": 4, "INFO": 2, "DEBUG": 1, "WARNING": 1, "missing": 1}),
])
def test_observe_file(file_name, file_format, pattern_p, group, result, build_file,monkeypatch, tmp_path, capsys):
    monkeypatch.chdir(tmp_path)
    pattern = re.compile(pattern_p)

    observe_file(file=file_name, formatter=file_format, p=pattern, group_by=group, interval=2, sleep=return_none,time_counter=get_next_number_of(), running_cond=get_running_cond())
    captured = capsys.readouterr()
    res = captured.out

    line1, line2 = res.strip().splitlines()
    res1 = json.loads(line1)
    res2 = json.loads(line2)
    assert res1 == result
    assert res2 == result



def return_new_file(tmp_path):
    p = tmp_path / "app1.log"
    lines = """DEBUG module2 asda
DEBUG module3 dsad
"""
    p.write_text(lines, encoding="utf-8")
    replace_list = []
    def replace_file(num):
        if len(replace_list) == 3:    
            os.replace("app1.log", "app.log")
        replace_list.append(1)    
    return replace_file

def get_next_number_of_rot():
    numbers = [0,1,2, 4, 6,7,8,9, 10, 20, 30]
    num = (i for i in numbers)
    def gen_number():
        return next(num)
    return gen_number

def get_running_cond_of_rot():
    conds = [True, True, True, True, True, True, False]
    cond = (i for i in conds)
    def get_cond():
        return next(cond)
    return get_cond

def test_observe_file_rotation(build_file,monkeypatch, tmp_path, capsys):
    monkeypatch.chdir(tmp_path)
    pattern = re.compile(r"(?P<level>\w+)\s+(?P<module>\S+)")

    observe_file(file="app.log", formatter=JsonFormat, p=pattern, group_by="level", interval=2, sleep=return_new_file(tmp_path),time_counter=get_next_number_of_rot(), running_cond=get_running_cond_of_rot())
    captured = capsys.readouterr()
    res = captured.out
    print(res)
    line1, line2, line3 = res.strip().splitlines()
    res1 = json.loads(line1)
    res2 = json.loads(line2)
    res3 = json.loads(line3)
    assert res1 == {"ERROR": 4, "INFO": 2, "DEBUG": 1, "WARNING": 1, "missing": 1}
    assert res2 == {"ERROR": 4, "INFO": 2, "DEBUG": 3, "WARNING": 1, "missing": 1}
    assert res3 == {"ERROR": 4, "INFO": 2, "DEBUG": 3, "WARNING": 1, "missing": 1}


@pytest.mark.parametrize("file,group,file_format,reg_pattern,result",[
    ("app.log", "level", "json1", r"(?P<level>\w+)\s+(?P<module>\S+)", "Invalid format: 'json1'\n"),
    ("app.log1", "level", "json", r"(?P<level>\w+)\s+(?P<module>\S+)", "app.log1 is not a file\n"),
    ("app.log", "none", "json", r"(?P<level>\w+)\s+(?P<module>\S+)", "Wrong group name, received: none, from pattern: {'level': 1, 'module': 2}\n")
])
def test_main(file,group,file_format,reg_pattern,result,tmp_path, build_file, monkeypatch, capsys):
    monkeypatch.chdir(tmp_path)
    monkeypatch.setattr(sys, "argv",["logtail.py", file, "--group-by", group, "--format", file_format, "--pattern", reg_pattern])
    with pytest.raises(SystemExit) as exc:
        main()
    res = capsys.readouterr()
    assert res.err == result
    assert exc.value.code == 2