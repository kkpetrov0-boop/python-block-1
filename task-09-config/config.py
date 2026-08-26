import configparser
import os
import json
import argparse
from pathlib import Path
from dataclasses import dataclass
import socket
from enum import StrEnum

@dataclass
class Resolved:
    value: ...
    source: str


@dataclass
class FieldSpec:
    name: str
    type_func: ...
    default: ...
    validator: ...


class LogLevel(StrEnum):
    DEBUG = "DEBUG"
    INFO = "INFO"
    WARNING = "WARNING"
    ERROR = "ERROR"


def in_range(low, high):
    def check(value):
        if not low <= value <= high:
            return f"must be between {low} and {high}"
        return None
    return check

def is_exist(path):
    if path.exists():
        return None
    return "Path doesn't exist"




FIELDS = [
    FieldSpec("port", Path, Path("/dev/ttyUSB0"), is_exist),
    FieldSpec("baud", int, 115200, in_range(300, 2_000_000)),
    FieldSpec("client_id", str, socket.gethostname(), None),
    FieldSpec("broker", str, "localhost", None),
    FieldSpec("broker_port", int, 1883, in_range(1, 65535)),
    FieldSpec("telemetry_topic", str, lambda cfg: f"fridge/{cfg['client_id']}/telemetry", None),
    FieldSpec("status_topic", str, lambda cfg: f"fridge/{cfg['client_id']}/status", None),
    FieldSpec("cmd_topic", str, lambda cfg: f"fridge/{cfg['client_id']}/cmd/setpoint", None),
    FieldSpec("buffer_path", str, "buffer.jsonl", None),
    FieldSpec("buffer_max_bytes", int, 200_000, in_range(100, 20_000_000)),
    FieldSpec("buffer_keep_lines", int, 500, in_range(10, 10_000)),
    FieldSpec("reconnect_min", float, 1, in_range(0.1, 100)),
    FieldSpec("reconnect_max", float, 60, in_range(10, 1000)),
    FieldSpec("mqtt_user", str, "", None),
    FieldSpec("mqtt_password", str, "", None),
    FieldSpec("log_level", LogLevel, LogLevel.INFO, None)
]


class ConfigError(Exception):
    pass

class ConfigFileError(ConfigError):
    pass

class ConfigTypeError(ConfigError):
    pass

class ConfigValidationError(ConfigError):
    pass


def cmd_parse() -> argparse.Namespace:
    parser = argparse.ArgumentParser(prog="config")
    parser.add_argument("--config", help="Takes argument for config (highest priority)")
    parser.add_argument("--port", help="USB port for ESP32", default=None)
    parser.add_argument("--baud", help="BAUD for UART", default=None)
    parser.add_argument("--client-id", help="CLIENT ID for MQTT broker", default=None)
    parser.add_argument("--broker", help="MQTT broker adress", default=None)
    parser.add_argument("--broker-port", help="Port for MQTT broker", default=None)
    parser.add_argument("--telemetry-topic", help="Topic for telemetry", default=None)
    parser.add_argument("--status-topic", help="Topic for status", default=None)
    parser.add_argument("--cmd-topic", help="Topic for cmd", default=None)
    parser.add_argument("--buffer-path", help="Path for buffer", default=None)
    parser.add_argument("--buffer-max-bytes", help="Max size of the buffer", default=None)
    parser.add_argument("--buffer-keep-lines", help="Set the number of lines to keep on overflow", default=None)
    parser.add_argument("--reconnect-min", help="Min time for reconnecting", default=None)
    parser.add_argument("--reconnect-max", help="Max time for reconnecting", default=None)
    parser.add_argument("--mqtt-user", help="Username for MQTT", default=None)
    parser.add_argument("--mqtt-password", help="Password for MQTT", default=None)
    parser.add_argument("--log-level", help="Level of loging", default=None)
    parser.add_argument("--explain", help="Show source for every config name", action="store_true")
    args = parser.parse_args()
    return args
 
def read_json(path):
    with open(path, "r") as file:
        json_dict = json.load(file)
    return json_dict

def read_ini(path):
    parser = configparser.ConfigParser()
    parser.read(path)
    ini_dict = {}
    for i in parser.sections():
        for k, v in parser[i].items():
            ini_dict[k] = v
    return ini_dict

def read_env():
    env_dict = {}
    env_dict["port"] = os.environ.get("FRIDGE_PORT", None)
    env_dict["baud"] = os.environ.get("FRIDGE_BAUD", None)
    env_dict["client_id"] = os.environ.get("FRIDGE_CLIENT_ID", None)
    env_dict["broker"] = os.environ.get("FRIDGE_BROKER", None)
    env_dict["broker_port"] = os.environ.get("FRIDGE_BROKER_PORT", None)
    env_dict["telemetry_topic"] = os.environ.get("FRIDGE_TELEMETRY_TOPIC", None)
    env_dict["status_topic"] = os.environ.get("FRIDGE_STATUS_TOPIC", None)
    env_dict["cmd_topic"] = os.environ.get("FRIDGE_CMD_TOPIC", None)
    env_dict["buffer_path"] = os.environ.get("FRIDGE_BUFFER", None)
    env_dict["buffer_max_bytes"] = os.environ.get("FRIDGE_BUFFER_MAX", None)
    env_dict["buffer_keep_lines"] = os.environ.get("FRIDGE_BUFFER_KEEP", None)
    env_dict["reconnect_min"] = os.environ.get("FRIDGE_RECONNECT_MIN", None)
    env_dict["reconnect_max"] = os.environ.get("FRIDGE_RECONNECT_MAX", None)
    env_dict["mqtt_user"] = os.environ.get("FRIDGE_MQTT_USER", None)
    env_dict["mqtt_password"] = os.environ.get("FRIDGE_MQTT_PASSWORD", None)
    return env_dict


def read_file(path):
    try:
        if path.suffix == ".json":
            try:
                file_dict = read_json(path)
            except json.JSONDecodeError as e:
                raise ConfigFileError(f"Unvalid json: {e}, {e.lineno=}")
        elif path.suffix == ".ini":
            try:
                file_dict = read_ini(path)
            except configparser.Error as e:
                raise ConfigFileError(f"Error in .ini file: {e}")
        elif path.suffix:
            raise ConfigFileError("Unknown extension")
        else:
            raise ConfigFileError("No extension")
    except OSError as e:
        raise ConfigFileError(f"File not found: {e}")
    return file_dict


def type_cast(dict_key, field):
    try:
        dict_key.value = field.type_func(dict_key.value)
    except ValueError as e:
        raise ConfigTypeError(f"Wrong type: {e}, {field.name}")
    return dict_key.value


def validate_field(complete_dict, field):
    error = None
    if field.validator is not None:
        error = field.validator(complete_dict[field.name].value)
    if error is not None:
        raise ConfigValidationError(f"{error}, {field.name}")
    return None


def assemble(cli_dict, env_dict, file_dict):
    complete_dict = {}
    errors = []
    for field in FIELDS:
        if field.name in cli_dict:
            resolved = Resolved(value=cli_dict[field.name], source="cli")
            complete_dict[field.name] = resolved
        elif field.name in env_dict and env_dict[field.name] is not None:
            resolved = Resolved(value=env_dict[field.name], source="env")
            complete_dict[field.name] = resolved
        elif field.name in file_dict and file_dict[field.name] is not None:
            resolved = Resolved(value=file_dict[field.name], source="file")
            complete_dict[field.name] = resolved
        else:
            if callable(field.default):
                flat = {name: r.value for name, r in complete_dict.items()}
                resolved = Resolved(value=field.default(flat), source="default")
            else:
                resolved = Resolved(value=field.default, source="default")
            complete_dict[field.name] = resolved

        try:
            type_cast(complete_dict[field.name], field)
        except ConfigTypeError as e:
            errors.append(str(e))
            continue

        try:
            validate_field(complete_dict, field)
        except ConfigValidationError as e:
            errors.append(str(e))

    return complete_dict, errors


def main():
    
    args = cmd_parse()

    cli_dict = {k: v for k, v in vars(args).items() if v is not None}
    env_dict = read_env()

    conf = cli_dict.get("config")
    if conf is None:
        file_dict = {}
    else:
        path = Path(conf)
        file_dict = read_file(path)
        

    complete_dict, errors = assemble(cli_dict, env_dict, file_dict)

    if errors:
        raise ConfigError(errors)
            
    if args.explain:
        for k, v in complete_dict.items():
            print(f"Value {k} was taken from {v.source}")

    
if __name__ == "__main__":
    main()