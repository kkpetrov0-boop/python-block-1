import struct
import math
from frames import ChecksumError, MalformedFrameError, UnknownFrameTypeError, parse_frame, FrameType, Frame, Telemetry, Status, Command
import pytest


def build_frame(type_code, test_frame):
    calculated_checksum = 0
    for n in test_frame:
        calculated_checksum ^= n
    frame = bytes([type_code]) + bytes([len(test_frame)]) + test_frame + bytes([calculated_checksum])
    return frame

def f32(num):
    num = struct.pack(">f", num)
    num = struct.unpack(">f", num)[0]
    return num

def test_checksum():
    test_telemetry = struct.pack(">bBffBB", 1, 9, 25.4, 24.4, 1, 9)
    test1 = parse_frame(test_telemetry)

    assert math.isclose(test1.temp, 25.4, rel_tol=1e-6)
    assert math.isclose(test1.setpoint, 24.4, rel_tol=1e-6)
    assert test1.comp_state == 1


@pytest.mark.parametrize("payload_exp,pack_args,type_code,result",[
    (">ffB", [25.4, 24.4, 1], FrameType.TELEMETRY, Telemetry(temp=f32(25.4), setpoint=f32(24.4), comp_state=1)),
    (">f", [10.0], FrameType.COMMAND, Command(setpoint=10.0)),
    (">B", [1], FrameType.STATUS, Status(status=1)),
    (">B", [0], FrameType.STATUS, Status(status=0))
])
def test_parsing(payload_exp,pack_args,type_code,result):
    payload = struct.pack(payload_exp, *pack_args)
    raw = build_frame(type_code, payload)
    parsed = parse_frame(raw)

    assert parsed == result


def test_checksum_error():
    with pytest.raises(ChecksumError, match="Wrong checksum: received"):
        test_telemetry = struct.pack(">bBffBB", 1, 9, 25.4, 24.4, 1, 8)
        parse_frame(test_telemetry)


def test_unknown_frame_type_error():
    with pytest.raises(UnknownFrameTypeError, match="Received unknown type:"):
        raw = build_frame(99, b"\x00" * 4)
        parse_frame(raw)


def test_malformed_frame_error():
    with pytest.raises(MalformedFrameError, match="Wrong length:"):
        raw = build_frame(1, b"\x00" * 4)
        parse_frame(raw)


def test_short_payload():
    with pytest.raises(MalformedFrameError, match="Wrong length"):
        raw = build_frame(FrameType.TELEMETRY, b"\x00" * 5)
        parse_frame(raw)


def test_type_error():
    with pytest.raises(TypeError, match="Frame"):
        Frame()
