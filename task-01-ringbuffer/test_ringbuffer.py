from RingBuffer import RingBuffer
import pytest

def test_ringbuffer_index():
    ringbuffer = RingBuffer(3)
    for i in range(10):
        ringbuffer.append(i*i)
    assert ringbuffer[-1] == 81
    assert list(ringbuffer) == [49, 64, 81]

def test_ringbuffer_extend():
    ringbuffer = RingBuffer(3)
    ringbuffer.extend([1,2,3,4])
    assert list(ringbuffer) == [2, 3, 4]
    assert len(ringbuffer) == 3

def test_ringbuffer_iter():
    ringbuffer = RingBuffer(3)
    ringbuffer.extend([1,2,3,4])
    length_1 = len(ringbuffer)
    list_1 = list(ringbuffer)
    list_2 = list(ringbuffer)
    length_2 = len(ringbuffer)
    assert length_1 == length_2
    assert list_1 == list_2

def test_ringbuffer_is_full():
    ringbuffer_2 = RingBuffer(2)
    assert not ringbuffer_2.is_full()
    ringbuffer_2.append(1)
    assert not ringbuffer_2.is_full()
    ringbuffer_2.append(1)
    assert ringbuffer_2.is_full()

def test_ringbuffer_clear():
    ringbuffer_3 = RingBuffer(3)
    ringbuffer_3.extend([1,2,3,4])
    ringbuffer_3.clear()
    assert len(ringbuffer_3) == 0
    assert not ringbuffer_3.is_full()
    ringbuffer_3.append(5)
    ringbuffer_3.append(6)
    ringbuffer_3.append(7)
    assert ringbuffer_3[0] == 5


def test_ringbuffer_errors():
    with pytest.raises(ValueError, match="Wrong capacity"):
        ringbuffer_2 = RingBuffer(0)
    with pytest.raises(IndexError, match="Index out of bounds"):    
        ringbuffer = RingBuffer(3)
        ringbuffer[5]
    with pytest.raises(IndexError, match="Index out of bounds"):    
        ringbuffer = RingBuffer(3)
        ringbuffer[-4]
