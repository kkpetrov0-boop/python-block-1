import time
from collections import deque
import sys

class RingBuffer:
    def __init__(self, capacity: int):
        if capacity < 1:
            raise ValueError("Wrong capacity")
        self.capacity = capacity
        self.values = []

        self._next = 0

    def __len__(self):
        return len(self.values)

    def __iter__(self):
        temp_list = [self[i] for i in range(len(self))]
        return iter(temp_list)

    def __getitem__(self, key):
        if key > len(self) - 1 or key < -len(self):
            raise IndexError("Index out of bounds")
        physindex = (key + self._next) % len(self)
        return self.values[physindex]

    def __repr__(self):
        temp_list = list(self)
        return f"{type(self).__name__}(capacity={self.capacity}, {temp_list})"

    def append(self, value):
        self._next %= self.capacity
        if len(self) < self.capacity:
            self.values.append(value)
        else:
            self.values[self._next]= value
        self._next += 1

    def extend(self, more_values):
        for value in more_values:
            self.append(value)

    def clear(self):
        self._next = 0
        self.values.clear()
        


    def is_full(self):
        return len(self) == self.capacity


ringbuffer = RingBuffer(100000)


for i in range(100000):
    ringbuffer.append(i)
time_ring_buffer = time.perf_counter()
for i in range(10000):
    ringbuffer[50000]
time__final_ring_buffer = time.perf_counter()


dq = deque(maxlen=100000)

for i in range(100000):
    dq.append(i)
time_dq = time.perf_counter()
for i in range(10000):
    dq[50000]
time__final_dq = time.perf_counter()
print((time__final_ring_buffer - time_ring_buffer)/10000)
print((time__final_dq - time_dq)/10000)
print(sys.getsizeof(ringbuffer.values))
print(sys.getsizeof(dq))