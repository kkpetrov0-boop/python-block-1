import time
import tracemalloc
from collections.abc import Iterator

def read_values_list(path) -> list[float]:
    with open(path, "r") as file:
        return [float(line) for line in file]
    

def read_values_gen(path) -> Iterator[float]:
    with open(path, "r") as file:
        for line in file:
            yield float(line)
    

def stop_tracking_mem() -> int:
    _current, peak = tracemalloc.get_traced_memory()
    tracemalloc.stop()
    return peak

def track_time(read_object_func, func, obj) -> str:
    t_start = time.perf_counter()
    func(read_object_func("text_file.txt"))
    time_stop = time.perf_counter()
    t_res = time_stop - t_start
    return f"{obj} {read_object_func.__name__}.{func.__name__}:\n time: {t_res}\n"

def track_mem(read_object_func, func, obj) -> str:
    tracemalloc.start()
    tracemalloc.reset_peak()
    func(read_object_func("text_file.txt"))
    peak = stop_tracking_mem()
    return f"{obj} {read_object_func.__name__}.{func.__name__}:\n memory: {peak}\n"

def track(func,read_object_func, obj) -> str:
    print(track_time(read_object_func, func, obj))
    print(track_mem(read_object_func, func, obj))



def main():
    track(sum, read_values_list, "List")
    track(max, read_values_list, "List")
    track(sum, read_values_gen, "Gen")
    track(max, read_values_gen, "Gen")



if __name__ == "__main__":
    main()