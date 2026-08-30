from pathlib import Path
from config import ConfigFileError, assemble
from config import read_file, in_range, is_exist, main, read_json, read_ini
import pytest
import sys
import json

import re


@pytest.fixture
def build_json(tmp_path):
    p = tmp_path / "app.json"
    lines = {
        "port": "COM3",
        "baud": 9600,
        "client_id": "fridge-01",
        "broker": "mqtt.local",
        "broker_port": 1884,
        "buffer_max_bytes": 500000,
        "buffer_keep_lines": 1000,
        "reconnect_min": 2.0,
        "reconnect_max": 120.0,
        "log_level": "DEBUG"
    }
    p.write_text(json.dumps(lines, indent=4), encoding="utf-8")
    return p

@pytest.fixture
def build_ini(tmp_path):
    p = tmp_path / "app.ini"
    lines = """
    [serial]
    port = COM3
    baud = 9600

    [mqtt]
    client_id = fridge-01
    broker = mqtt.local
    broker_port = 1884
    mqtt_user = gateway
    mqtt_password = secret

    [buffer]
    buffer_max_bytes = 500000
    buffer_keep_lines = 1000

    [logging]
    log_level = DEBUG
    """
    
    p.write_text(lines, encoding="utf-8")
    return p


@pytest.fixture
def build_json_er(tmp_path):
    p = tmp_path / "app_error.json"
    lines_json = "port = COM3"
    p.write_text(lines_json, encoding="utf-8")
    return p

@pytest.fixture
def build_ini_er(tmp_path):
    p = tmp_path / "app_error.ini"
    lines = """
        [serial
        port = COM3
        baud = 9600"""
    
    p.write_text(lines, encoding="utf-8")
    return p



def test_json(build_json, tmp_path, monkeypatch):
    monkeypatch.chdir(tmp_path)
    p = {
        "port": "COM3",
        "baud": 9600,
        "client_id": "fridge-01",
        "broker": "mqtt.local",
        "broker_port": 1884,
        "buffer_max_bytes": 500000,
        "buffer_keep_lines": 1000,
        "reconnect_min": 2.0,
        "reconnect_max": 120.0,
        "log_level": "DEBUG"
    }
    assert read_json("app.json") == p





def test_ini(build_ini, tmp_path, monkeypatch):
    monkeypatch.chdir(tmp_path)
    p = {
        "port": "COM3",
        "baud": "9600",
        "client_id": "fridge-01",
        "broker": "mqtt.local",
        "broker_port": "1884",
        "mqtt_user": "gateway",
        "mqtt_password": "secret",
        "buffer_max_bytes": "500000",
        "buffer_keep_lines": "1000",
        "log_level": "DEBUG",
    }
    assert read_ini("app.ini") == p 



@pytest.mark.parametrize("min,max,val,res",[
    (0, 100, 110, "must be between 0 and 100"),
    (0, 100, 0, None),
    (0, 100, 100, None),
    (0, 100, 50, None),
    (0, 100, -5, "must be between 0 and 100"),
])
def test_in_range(min,max,val,res,capsys):
    result = in_range(min, max)(val)
    assert result == res


def test_main(tmp_path,monkeypatch,capsys):
    monkeypatch.chdir(tmp_path)
    p = tmp_path / "dev"
    p.mkdir(parents=True,exist_ok=True)
    p = p / "ttyUSB0"
    p.write_text("String for port", encoding="utf-8")
    monkeypatch.setattr(sys, "argv", ["config.py", "--port", str(p), "--explain"])
    with pytest.raises(SystemExit) as exc:
        main()
    result = capsys.readouterr()
    assert "Value port was taken from cli" in result.out
    assert exc.value.code == 0


def test_config_error(tmp_path,monkeypatch,capsys, build_ini_er):
    monkeypatch.chdir(tmp_path)
    monkeypatch.setattr(sys, "argv", ["config.py", "--port", "no_such_file", "--explain"])
    with pytest.raises(SystemExit) as exc:
        main()
    result = capsys.readouterr()
    assert result.err == "Path doesn't exist, port\n"
    assert exc.value.code == 2

    monkeypatch.setattr(sys, "argv", ["config.py", "--config", str(build_ini_er), "--explain"])
    with pytest.raises(SystemExit) as exc:
        main()
    result = capsys.readouterr()
    assert "Error in .ini file" in result.err
    assert exc.value.code == 2
    

#@pytest.mark.parametrize()
def test_read_file(build_ini, build_json, build_ini_er, build_json_er, tmp_path, monkeypatch, capsys):
    monkeypatch.chdir(tmp_path)
    assert read_file(build_ini) == {'port': 'COM3', 'baud': '9600', 'client_id': 'fridge-01', 'broker': 'mqtt.local', 'broker_port': '1884', 'mqtt_user': 'gateway', 'mqtt_password': 'secret', 'buffer_max_bytes': '500000', 'buffer_keep_lines': '1000', 'log_level': 'DEBUG'}
    assert read_file(build_json) == {'port': 'COM3', 'baud': 9600, 'client_id': 'fridge-01', 'broker': 'mqtt.local', 'broker_port': 1884, 'buffer_max_bytes': 500000, 'buffer_keep_lines': 1000, 'reconnect_min': 2.0, 'reconnect_max': 120.0, 'log_level': 'DEBUG'}
    with pytest.raises(ConfigFileError, match="File not found:") as e:
        assert read_file(Path("no_such_file.json"))
    with pytest.raises(ConfigFileError, match="No extension") as e:
        assert read_file(Path("no_such_file"))
    with pytest.raises(ConfigFileError, match="Unknown extension") as e:
        assert read_file(Path("no_such_file.txt"))
    with pytest.raises(ConfigFileError, match=re.escape("Error in .ini file")) as e:
        assert read_file(build_ini_er)
    with pytest.raises(ConfigFileError, match="Invalid json") as e:
        assert read_file(build_json_er)
    

@pytest.mark.parametrize("cli_dict,env_dict,file_dict,fields,result",[
    ({"port": "COM3"},{"port": "COM4"},{"port": "COM5"},["port"],["cli"]),
    ({"port": "COM3"}, {"baud": "110000"}, {"reconnect_min": "5"}, ["baud","reconnect_min", "broker_port"], ["env", "file", "default"])
])
def test_assemble_source(cli_dict, env_dict, file_dict, fields, result):
    complete_dict, errors = assemble(cli_dict, env_dict, file_dict)
    for index, field in enumerate(fields):
        assert complete_dict[field].source == result[index]


@pytest.mark.parametrize("cli_dict,env_dict,file_dict,fields,result",[
    ({"broker_port": "50"},{},{"port": "COM3"},["broker_port","port"],[50, Path("COM3")]),
    ({"port": "COM3"}, {}, {"broker_port": "50"}, ["broker_port","port"],[50, Path("COM3")])
])
def test_assemble_value(cli_dict, env_dict, file_dict, fields, result):
    complete_dict, errors = assemble(cli_dict, env_dict, file_dict)
    for index, field in enumerate(fields):
        assert complete_dict[field].value == result[index]

def test_errors_counter():
    cli_dict = {"baud": "100", "broker_port": "String", "port": "Not exist"}
    env_dict = {}
    file_dict = {}
    complete_dict, errors = assemble(cli_dict, env_dict, file_dict)
    assert "port" in errors[0] and "baud" in errors[1] and "broker_port" in errors[2], "Wrong errors"
    assert len(errors) == 3, "Wrong errors counter"


