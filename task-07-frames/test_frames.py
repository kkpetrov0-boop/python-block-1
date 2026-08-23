import struct
import math
from frames import ChecksumError, MalformedFrameError, UnknownFrameTypeError, parse_frame, FrameType, Frame


def build_frame(type_code, test_frame):
    calculated_checksum = 0
    for n in test_frame:
        calculated_checksum ^= n
    frame = bytes([type_code]) + bytes([len(test_frame)]) + test_frame + bytes([calculated_checksum])
    return frame

test_telemetry = struct.pack(">bBffBB", 1, 9, 25.4, 24.4, 1, 9)
#print(repr(parse_frame(test_telemetry)))
test1 = parse_frame(test_telemetry)

assert math.isclose(test1.temp, 25.4, rel_tol=1e-6), "Wrong temperature in telemetry"
assert math.isclose(test1.setpoint, 24.4, rel_tol=1e-6), "Wrong setpoint in telemetry"
assert test1.comp_state == 1, "Wrong compressor state in telemetry"

payload = struct.pack(">ffB", 25.4, 24.4, 1)
raw = build_frame(FrameType.TELEMETRY, payload)
parsed = parse_frame(raw)

assert math.isclose(parsed.temp, 25.4, rel_tol=1e-6), "Wrong temperature in telemetry(auto)"
assert math.isclose(parsed.setpoint, 24.4, rel_tol=1e-6), "Wrong setpoint in telemetry(auto)"
assert parsed.comp_state == 1, "Wrong compressor state in telemetry(auto)"

payload = struct.pack(">f", 10.0)
raw = build_frame(FrameType.COMMAND, payload)
parsed = parse_frame(raw)
assert math.isclose(parsed.setpoint, 10.0, rel_tol=1e-6), "Wrong setpoint in command"

payload = struct.pack(">B", 1)
raw = build_frame(FrameType.STATUS, payload)
parsed = parse_frame(raw)
assert parsed.status == 1, "Wrong status in status (on)"
payload = struct.pack(">B", 0)
raw = build_frame(FrameType.STATUS, payload)
parsed = parse_frame(raw)
assert parsed.status == 0, "Wrong status in status (off)"

try:
    test_telemetry = struct.pack(">bBffBB", 1, 9, 25.4, 24.4, 1, 8)
    test1 = parse_frame(test_telemetry)
    assert False, "No checksum error"
except ChecksumError as e:
    pass

try:
    raw = build_frame(99, b"\x00" * 4)
    parsed = parse_frame(raw)
    assert False, "No UnknownFrameTypeError"
except UnknownFrameTypeError as e:
    pass

try:
    raw = build_frame(1, b"\x00" * 4)
    parse_frame(raw)
    assert False, "No MalformedFrameError"
except MalformedFrameError as e:
    pass

try:
    raw = build_frame(FrameType.TELEMETRY, b"\x00" * 5)
    parse_frame(raw)
    assert False, "No MalformedFrameError on short payload"
except MalformedFrameError as e:
    pass

try:
    Frame()
    assert False, "Class Frame() is instantiatable"
except TypeError as e:
    pass