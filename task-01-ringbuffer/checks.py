from RingBuffer import RingBuffer

ringbuffer = RingBuffer(3)

for i in range(10):
    ringbuffer.append(i*i)
assert ringbuffer[-1] == 81, "Wrong access on index -1"
assert list(ringbuffer) == [49, 64, 81], "Wrong order"

ringbuffer.extend([1,2,3,4])
assert list(ringbuffer) == [2, 3, 4], "Invalid extend"
assert len(ringbuffer) == 3, "Wrong length"

length_1 = len(ringbuffer)
list_1 = list(ringbuffer)
list_2 = list(ringbuffer)
length_2 = len(ringbuffer)
assert length_1 == length_2, "Iteration breaks the len func"
assert list_1 == list_2, "Iteration gives invalid result"

list_3 = [ringbuffer[i % 3] for i in range(6)]
assert list_3[0:3] == list_3[3:6], "Iteration gives invalid result"
    
try:
    ringbuffer_2 = RingBuffer(0)
    assert False, "No ValueError"
except ValueError:
    pass
try:
    ringbuffer[5]
    assert False, "No IndexError"
except IndexError:
    pass
try:
    ringbuffer[-4]
    assert False, "No IndexError (negative)"
except IndexError:
    pass

ringbuffer_2 = RingBuffer(2)
assert not ringbuffer_2.is_full(), "Empty but return full"
ringbuffer_2.append(1)
assert not ringbuffer_2.is_full(), "Return full, while not"
ringbuffer_2.append(1)
assert ringbuffer_2.is_full(), "Return not full, while full"

ringbuffer_3 = RingBuffer(3)
ringbuffer_3.extend([1,2,3,4])
ringbuffer_3.clear()
assert len(ringbuffer_3) == 0, "Not cleared"
assert not ringbuffer_3.is_full(), "Empty but return full"
ringbuffer_3.append(5)
ringbuffer_3.append(6)
ringbuffer_3.append(7)
assert ringbuffer_3[0] == 5, "Wrong append/getitem after clear"
