from log_rotator import create_plan, exec_plan
import tempfile
from pathlib import Path

with tempfile.TemporaryDirectory() as tmp:
    base = Path(tmp)
    (base / "app.log").write_bytes(b"x" * 2_000_000)
    (base / "small.log").write_bytes(b"x" * 100)
    names = sorted(p.name for p in base.iterdir())
    plan = create_plan(base, keep=10, max_size=1)
    plan_names = sorted(p.name for p in base.iterdir())
    assert names == plan_names, "Plan func changed something"
    assert plan[0].kind == "archive" and plan[0].source.name == "app.log" and plan[0].destination.suffix == ".gz", "Wrong plan"
    assert len(plan) == 1, "Size filter is not working"


with tempfile.TemporaryDirectory() as tmp:
    base = Path(tmp)
    file = base / "app.log"
    (file).write_bytes(b"x" * 2_000_000)
    plan = create_plan(base, keep=10, max_size=1)
    exec_plan(plan, base)
    new_plan = create_plan(base, keep=10, max_size=1)
    assert new_plan == [], "Idempotency error"
    assert not file.exists(), "File was not deleted"
    dst = next(i for i in plan if i.kind == "archive")
    assert dst.destination.exists(), "No archive after plan exec"

with tempfile.TemporaryDirectory() as tmp:
    base = Path(tmp)
    for i in range(1, 8):
        file_name = "app.log.20260" + str(i) + "01000000.gz"
        file = base / file_name
        (file).write_bytes(b"x" * 2_000_000)
    plan = create_plan(base, keep=3, max_size=1)
    exec_plan(plan, base)
    paths = list(Path(base).rglob("*.gz"))
    assert len(paths) == 3, "Keep flag is not working"
    names = sorted(p.name for p in paths)
    assert names == ["app.log.20260501000000.gz", "app.log.20260601000000.gz", "app.log.20260701000000.gz"],"Wrong keeped files"

def broken_copy(src, dst):
    raise OSError("simulated interruption")

with tempfile.TemporaryDirectory() as tmp:
    base = Path(tmp)
    file = base / "app.log"
    (file).write_bytes(b"x" * 2_000_000)
    plan = create_plan(base, keep=10, max_size=1)
    try:
        exec_plan(plan, base, broken_copy)
        assert False, "No error raised"
    except OSError as e:
        pass
    assert file.exists(), "File was deleted before replacement"
    paths = list(Path(base).rglob("*.gz"))
    assert paths == [], "Archive appeared before tmp file"