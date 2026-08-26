from pathlib import Path
from config import ConfigFileError, assemble
from config import read_file

cli_dict = {"port": "COM3"}
env_dict = {"port": "COM4"}
file_dict = {"port": "COM5"}
complete_dict, errors = assemble(cli_dict, env_dict, file_dict)
assert complete_dict["port"].source == "cli","Wrong priority"

cli_dict = {"baud": "100", "broker_port": "String", "port": "Not exist"}
env_dict = {}
file_dict = {}
complete_dict, errors = assemble(cli_dict, env_dict, file_dict)
assert "port" in errors[0] and "baud" in errors[1] and "broker_port" in errors[2], "Wrong errors"
assert len(errors) == 3, "Wrong errors counter"

try:
    read_file(Path(__file__).parent / "broken.json")
    assert False, "Missing ConfigFileError"
except ConfigFileError:
    pass

cli_dict = {"port": "COM3"}
env_dict = {"baud": "110000"}
file_dict = {"reconnect_min": "5"}
complete_dict, errors = assemble(cli_dict, env_dict, file_dict)
assert complete_dict["baud"].source == "env", "Wrong source"
assert complete_dict["reconnect_min"].source == "file", "Wrong source"
assert complete_dict["broker_port"].source == "default", "Wrong source"

cli_dict = {"broker_port": "50"}
env_dict = {}
file_dict = {"port": "COM3"}
complete_dict, errors = assemble(cli_dict, env_dict, file_dict)
assert complete_dict["broker_port"].value == 50, "Wrong value"
assert complete_dict["port"].value == Path("COM3"), "WrongValue"

cli_dict = {"port": "COM3"}
env_dict = {}
file_dict = {"broker_port": "50"}
complete_dict, errors = assemble(cli_dict, env_dict, file_dict)
assert complete_dict["broker_port"].value == 50, "Wrong value"
assert complete_dict["port"].value == Path("COM3"), "WrongValue"