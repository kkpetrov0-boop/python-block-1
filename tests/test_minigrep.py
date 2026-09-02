from log_utilities.minigrep import search_in_text, process, main
import re
import subprocess, sys
import pytest
from pathlib import Path
from argparse import Namespace

@pytest.mark.parametrize("regexp,ignorecase,lines,invert,result",[
    ("error", 0, ["a error b", "clean"], False, [(1, "a error b")]),
    ("error", 0, ["a error b", "clean"], True, [(2, "clean")]),
    ("error", re.IGNORECASE, ["a ErRoR b", "clean"], False, [(1, "a ErRoR b")])
])
def test_search_in_text(regexp, ignorecase, lines, invert, result):
    prog = re.compile(regexp, ignorecase)
    calc = search_in_text(prog, lines, invert)
    assert calc == result


@pytest.fixture
def run_minigrep(tmp_path):
    def run(*args, **kwargs):
        return subprocess.run(
            [sys.executable, "-m", "log_utilities.minigrep", *args],
            capture_output=True, text=True, cwd=tmp_path, **kwargs
        )
    return run

@pytest.fixture
def build_tmp_files(tmp_path):
    p1 = tmp_path / "app.log"
    p2 = tmp_path / "app_copy.log"
    lines1 = [
                "Oh my god an ErRor occured",
                "Oh my god an erroR occured",
                "Oh my god an  occured",
                "error",
                "no nothing",
                "ERROR"
            ]
    lines2 = [
        "Oh my god an ERRor occured",
        "Oh my god an eRroR occured",
        "error",
        "Oh my god an  occured",
        "123",
        "no nothing",
        "ERROR",
    ]
    p1.write_text("\n".join(lines1), encoding="utf-8")
    p2.write_text("\n".join(lines2), encoding="utf-8")
    return p1, p2


def test_program1(build_tmp_files, run_minigrep, tmp_path):
    r = run_minigrep("error", "app.log")
    assert r.returncode == 0
    assert "error" in r.stdout
    assert r.stderr == ""

def test_program2(build_tmp_files, run_minigrep, tmp_path):
    p1, p2 = build_tmp_files
    with p1.open("r", encoding="utf-8") as file:
        r = run_minigrep("error", "-n", "-i", stdin=file)
    
    assert r.returncode == 0
    assert "1: Oh my god an ErRor occured" in r.stdout
    assert "2: Oh my god an erroR occured" in r.stdout
    assert "4: error" in r.stdout
    assert "6: ERROR" in r.stdout
    assert r.stderr == ""


def test_program3(build_tmp_files,run_minigrep, tmp_path):
    expected_lines = ["app.log:Oh my god an ErRor occured",
                        "app.log:Oh my god an erroR occured",
                        "app.log:Oh my god an  occured",
                        "app.log:no nothing",
                        "app.log:ERROR",
                        "app_copy.log:Oh my god an ERRor occured",
                        "app_copy.log:Oh my god an eRroR occured",
                        "app_copy.log:Oh my god an  occured",
                        "app_copy.log:123",
                        "app_copy.log:no nothing",
                        "app_copy.log:ERROR"]
    r = run_minigrep("-v", "error", "app.log", "app_copy.log")
    assert r.stdout.splitlines() == expected_lines


def test_program4(build_tmp_files,run_minigrep, tmp_path):
    r = run_minigrep("-c", "error", "*.log")
    assert r.returncode == 0
    assert "app.log:1" in r.stdout
    assert "app_copy.log:1" in r.stdout
    assert r.stderr == ""

@pytest.mark.parametrize("reg_expres,file", [
    ("[", "app.log"),
    ("error", "nosuchfile.log")
])
def test_program5(run_minigrep, reg_expres, file):
    r = run_minigrep(reg_expres, file)
    assert r.returncode == 2
    assert r.stdout == ""


@pytest.mark.parametrize("line_num_flag,count_flag,result_out", [
    (True, False, "app.log:4: error\n"),
    (False, False, "app.log:error\n"),
    (True, True, "app.log:1\n"),
])
def test_process(
        line_num_flag,
        count_flag,
        result_out,
        build_tmp_files, tmp_path, capsys):
    p1, p2 = build_tmp_files
    process_fix = Namespace(inverse=False, line_number=line_num_flag, count=count_flag, pattern="error", file=p1)
    with p1.open("r", encoding="utf-8") as file:
        result = process(re.compile("error"), p1.name, file, process_fix, True)
        captured = capsys.readouterr()
        assert captured.out == result_out
        assert captured.err == ""
        assert result == True



@pytest.mark.parametrize("reg_exp,file_sign,result_out,result_err,exit_code", [
    ("error", "*.log", "app.log:error\napp_copy.log:error\n","", 0),
    ("[", "app.log", "","Invalid regular expression: unterminated character set at 0\n", 2),
    ("error", "nosuchfile.log", "","minigrep: nosuchfile.log: No such file or directory\n", 2),
    ("error", "*.txt", "","Can not find a file: *.txt\n", 2),
])
def test_main(
    reg_exp,
    file_sign,
    result_out,
    result_err,
    exit_code,
    tmp_path, monkeypatch, capsys, build_tmp_files):
    
    monkeypatch.chdir(tmp_path)
    monkeypatch.setattr(sys, "argv", ["minigrep", reg_exp, file_sign])
    with pytest.raises(SystemExit) as exc:
        main()
    result = capsys.readouterr()
    assert exc.value.code == exit_code
    assert result.out == result_out
    assert result.err == result_err
