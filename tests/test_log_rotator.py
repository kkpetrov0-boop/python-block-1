from log_utilities.log_rotator import create_plan, exec_plan
import tempfile
from pathlib import Path
import pytest


def test_dry_run_changes_nothing(tmp_path):
    (tmp_path / "app.log").write_bytes(b"x" * 2_000_000)
    (tmp_path / "small.log").write_bytes(b"x" * 100)
    names = sorted(p.name for p in tmp_path.iterdir())
    plan = create_plan(tmp_path, keep=10, max_size=1)
    plan_names = sorted(p.name for p in tmp_path.iterdir())
    assert names == plan_names, "Plan func changed something"
    assert plan[0].kind == "archive" and plan[0].source.name == "app.log" and plan[0].destination.suffix == ".gz", "Wrong plan"
    assert len(plan) == 1, "Size filter is not working"

def test_idempotency(tmp_path):
    file = tmp_path / "app.log"
    (file).write_bytes(b"x" * 2_000_000)
    plan = create_plan(tmp_path, keep=10, max_size=1)
    exec_plan(plan, tmp_path)
    new_plan = create_plan(tmp_path, keep=10, max_size=1)
    assert new_plan == [], "Idempotency error"
    assert not file.exists(), "File was not deleted"
    dst = next(i for i in plan if i.kind == "archive")
    assert dst.destination.exists(), "No archive after plan exec"

def test_keep_flag(tmp_path):
    for i in range(1, 8):
        file_name = "app.log.20260" + str(i) + "01000000.gz"
        file = tmp_path / file_name
        (file).write_bytes(b"x" * 2_000_000)
    plan = create_plan(tmp_path, keep=3, max_size=1)
    exec_plan(plan, tmp_path)
    paths = list(Path(tmp_path).rglob("*.gz"))
    assert len(paths) == 3, "Keep flag is not working"
    names = sorted(p.name for p in paths)
    assert names == ["app.log.20260501000000.gz", "app.log.20260601000000.gz", "app.log.20260701000000.gz"],"Wrong keeped files"

def broken_copy(src, dst):
    raise OSError("simulated interruption")

def test_interruption(tmp_path):
    file = tmp_path / "app.log"
    (file).write_bytes(b"x" * 2_000_000)
    plan = create_plan(tmp_path, keep=10, max_size=1)
    with pytest.raises(OSError, match="simulated interruption"):
        exec_plan(plan, tmp_path, broken_copy)
    assert file.exists(), "File was deleted before replacement"
    paths = list(Path(tmp_path).rglob("*.gz"))
    assert paths == [], "Archive appeared before tmp file"