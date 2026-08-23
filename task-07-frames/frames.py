from dataclasses import dataclass
import struct
from abc import ABC, abstractmethod
from enum import IntEnum
import logging


logger = logging.getLogger(__name__)

class_dict = {}

class FrameType(IntEnum):
    TELEMETRY = 1
    COMMAND = 2
    STATUS = 3


class Frame(ABC):
    @classmethod
    @abstractmethod
    def from_bytes(cls, payload) -> "Frame":
        ...

    def __init_subclass__(cls):
        global class_dict
        class_name = cls.class_name
        class_dict[class_name.value] = cls


@dataclass
class Telemetry(Frame):
    temp: float
    setpoint: float
    comp_state: int
    class_name = FrameType.TELEMETRY
    format = ">ffB"

    @classmethod
    def from_bytes(cls, payload):
        try:
            temp, setpoint, comp_state = struct.unpack(cls.format, payload)
        except struct.error as e:
            raise MalformedFrameError(f"Wrong length: {e}")
        return cls(temp, setpoint, comp_state)

@dataclass
class Command(Frame):
    setpoint: float
    class_name = FrameType.COMMAND
    format = ">f"

    @classmethod
    def from_bytes(cls, payload):
        try:
            setpoint = struct.unpack(cls.format, payload)[0]
        except struct.error as e:
            raise MalformedFrameError(f"Wrong length: {e}")
        return cls(setpoint)

@dataclass
class Status(Frame):
    status: int
    class_name = FrameType.STATUS
    format =  ">B"

    @classmethod
    def from_bytes(cls, payload):
        try:
            status = struct.unpack(cls.format, payload)[0]
        except struct.error as e:
            raise MalformedFrameError(f"Wrong length: {e}")
        return cls(status)

class FrameError(Exception):
    pass
class MalformedFrameError(FrameError):
    pass
class ChecksumError(FrameError):
    pass
class UnknownFrameTypeError(FrameError):
    pass

test_bytes = b'\x01\tA\xcb33A\xc333\x01\t'
fake_test_bytes = b'\x01\x08A\xcb33A\xc333\x01\x00\x01'

def parse_frame(raw):
    if len(raw) < 3:
        raise MalformedFrameError(f"Wrong length: length < 3")
    frame_type = raw[0]
    length = raw[1]
    if not length == (len(raw) - 3):
        raise MalformedFrameError(f"Wrong length: received={length} calculated={len(raw) -3}")
    received_checksum = raw[-1]
    calculated_checksum = 0
    for n in raw[2:-1]:
        calculated_checksum ^= n
    if not received_checksum == calculated_checksum:
        raise ChecksumError(f"Wrong checksum: received={received_checksum}, calculated={calculated_checksum}")
    try:
        mark = class_dict[frame_type]
    except KeyError:
        raise UnknownFrameTypeError(f"Received unknown type: received={frame_type}, has={class_dict}")
    payload = raw[2:-1]
    frame_type = mark.from_bytes(payload)
    return frame_type
    


def main():
    test = None
    try:
        test = parse_frame(test_bytes)
    except (MalformedFrameError, ChecksumError, UnknownFrameTypeError) as e:
        logger.error(f"{e}")
    if test:
        print(class_dict)
        print(repr(test))
       # Frame()


if __name__ == "__main__":
    main()