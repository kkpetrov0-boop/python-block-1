from minigrep import search_in_text
import re
import subprocess, sys

prog = re.compile("error")
result = search_in_text(prog, ["a error b", "clean"], False)
assert result == [(1, "a error b")], "Wrong basic search in text logic or numeration"
result = search_in_text(prog, ["a error b", "clean"], True)
assert result == [(2, "clean")], "Wrong inverse search in text logic"
prog = re.compile("error", re.IGNORECASE)
result = search_in_text(prog, ["a ErRoR b", "clean"], False)
assert result == [(1, "a ErRoR b")], "IGNORECASE is not working"

r = subprocess.run(
    [sys.executable, "minigrep.py", "error", "app.log"],
    capture_output=True, text=True 
)
assert r.returncode == 0, "Wrong return code on correct input"
assert "error" in r.stdout, "Correct result is not in stdout"
assert r.stderr == "", "Stderr is not empty on correct input"

with open("app.log", "r", encoding="utf-8") as file:
    r = subprocess.run(
        [sys.executable, "minigrep.py", "-n", "-i", "error"],
        stdin=file, capture_output=True, text=True
    )
assert r.returncode == 0, "Wrong return code on file as an input"
assert "1: Oh my god an ErRor occured" in r.stdout,"Correct result is not in stdout"
assert "2: Oh my god an erroR occured" in r.stdout,"Correct result is not in stdout"
assert "4: error" in r.stdout,"Correct result is not in stdout"
assert "6: ERROR" in r.stdout,"Correct result is not in stdout"
assert r.stderr == "", "Stderr is not empty file as an input"

r = subprocess.run(
    [sys.executable, "minigrep.py", "-v", "error", "app.log", "app_copy.log"],
    capture_output=True, text=True 
)

assert r.returncode == 0, "Wrong return code on multiple files as an input"
assert "app.log:error" not in r.stdout, "-v is not working"
assert "app.log:Oh my god an ErRor occured" in r.stdout,"Correct result is not in stdout"
assert "app.log:Oh my god an erroR occured" in r.stdout,"Correct result is not in stdout"
assert "app.log:Oh my god an  occured" in r.stdout,"Correct result is not in stdout"
assert "app.log:no nothing" in r.stdout,"Correct result is not in stdout"
assert "app.log:ERROR" in r.stdout,"Correct result is not in stdout"
assert "app_copy.log:Oh my god an ERRor occured" in r.stdout,"Correct result is not in stdout"
assert "app_copy.log:Oh my god an eRroR occured" in r.stdout,"Correct result is not in stdout"
assert "app_copy.log:Oh my god an  occured" in r.stdout,"Correct result is not in stdout"
assert "app_copy.log:123" in r.stdout,"Correct result is not in stdout"
assert "app_copy.log:no nothing" in r.stdout,"Correct result is not in stdout"
assert "app_copy.log:ERROR" in r.stdout,"Correct result is not in stdout"
assert r.stderr == "", "Stderr is not empty multiple files as an input"

r = subprocess.run(
    [sys.executable, "minigrep.py", "-c", "error", "*.log"],
    capture_output=True, text=True 
)
assert r.returncode == 0, "Wrong return code on counting through multiple files"
assert "app.log:1" in r.stdout, "Correct result is not in stdout"
assert "app_copy.log:1" in r.stdout, "Correct result is not in stdout"
assert r.stderr == "", "Stderr is not empty on counting through multiple files"

r = subprocess.run(
    [sys.executable, "minigrep.py", "[", "app.log"],
    capture_output=True, text=True 
)
assert r.returncode == 2, "Wrong return code on invalid regex"
assert r.stdout == "", "Stdout is not empty"
assert "Invalid regular expression: unterminated character set at 0" in r.stderr, "Error is not in stderr"

r = subprocess.run(
    [sys.executable, "minigrep.py", "error", "nosuchfile.log"],
    capture_output=True, text=True 
)
assert r.returncode == 2, "Wrong return code on missing file"
assert r.stdout == "", "Stdout is not empty"
assert "minigrep: nosuchfile.log: No such file or directory" in r.stderr, "Error is not in stderr"