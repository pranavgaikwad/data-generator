#!/usr/bin/env python

import os
import re
import math
import random
import string
import argparse
from collections import deque

UNITS = ["b", "Ki", "Mi", "Gi", "Ti"]

def create_binary_file(size: int, path: str, mode: str = "wb+") -> int:
    try:
        with open(path, mode) as f:
            f.write(os.urandom(size))
        print("Created file {filename} of size {size} bytes".format(filename=path, size=size))
    except Exception as e:
        print("Failed writing file {}".format(str(e)))
        return -1
    return 0

def create_random_files(total_size: int, min_files: int, max_files: int, dest: str) -> int:
    loop_breaker = deque(10*[random.randrange(1, 100000)], maxlen=10)
    total_created = 0
    while (int(total_size) > 0) and (total_created <= max_files):
        isLastFile = lambda created, total: True if (total-created==1) else False
        total_remaining = max(min_files - total_created, 0)
        max_size = int(total_size / total_remaining) if total_remaining != 0 else total_size
        if max_size < 2:
            break
        current_file_size = total_size if isLastFile(total_created, max_files) else random.randrange(1, max_size)
        current_file_name = ''.join(random.choice(string.ascii_lowercase) for i in range(random.randrange(4, 10)))
        current_file_path = "{directory}/{file_name}".format(directory=dest, file_name=current_file_name)
        rc = create_binary_file(int(current_file_size), current_file_path)
        total_created += 1 if rc == 0 else 0
        total_size -= current_file_size if rc == 0 else 0
        loop_breaker.append(total_size)
        # break loop if last 10 values have been consistently same, indicates problem creating files
        xor_result = 0
        for q_item in loop_breaker:
            xor_result ^= int(q_item)
        if xor_result == 0:
            print("Detected infinite loop. Breaking...")
            break
    return total_created

def is_unit_supported(unit: str):
    return True if UNITS.index(unit) != -1 else False

def validate_size(size: str):
    try: 
        _, unit = int(re.match(r'(\d+)(\w+)', size)[1]), re.match(r'(\d+)(\w+)', size)[2]
        if not is_unit_supported(unit):
            raise ValueError
    except:
        raise ValueError
    return size

def in_bytes(number: int, unit: str) -> int:
    base = 1000
    exponent = UNITS.index(unit) if UNITS.index(unit) != -1 else 1
    return math.pow(base, exponent) * number


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--size", help="total size of random data in supported units: {}".format(','.join(UNITS)), type=validate_size, required=True)
    parser.add_argument("--max-files", help="maximum number of files to create", type=int, required=True)
    parser.add_argument("--min-files", help="minimum number of files to create", default=1, type=int)
    parser.add_argument("--dest-dir", help="destination directory", type=str, required=True)
    args = parser.parse_args()
    size, unit =  re.match(r'(\d+)(\w+)', args.size)[1], re.match(r'(\d+)(\w+)', args.size)[2]
    size_in_bytes = in_bytes(int(size), unit)
    created = create_random_files(size_in_bytes, args.min_files, args.max_files, args.dest_dir)
    print("Created {} random files".format(created))
    while True:
        pass