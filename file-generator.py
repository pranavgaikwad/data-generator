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
    generated_size = 0
    data = b''
    while generated_size < size:
        generated_size = random.randint(min(size-generated_size, 10), size-generated_size)
        data += os.urandom(generated_size) + bytes("\n", encoding='utf8')
        generated_size += generated_size
    return write_to_file(data, path, mode)

def write_to_file(data: bytes, path: str, mode: str) -> int:
    try:
        with open(path, mode) as f:
            f.write(data)
        print("Created file {} of size {}".format(path, to_si(len(data))))
    except Exception as e:
        print("Failed writing file {}".format(str(e)))
        return -1
    return 0 

def read_from_file(path: str) -> str:
    data = ""
    try:
        with open(path, "r") as f:
            data = f.read()
    except Exception as e:
        print("Failed reading file {}".format(str(e)))
    return data

def create_random_files(total_size: int, min_files: int, max_files: int, dest: str) -> int:
    loop_breaker = deque(10*[random.randrange(1, 100000)], maxlen=10)
    total_created = 0
    while (int(total_size) > 0) and (total_created <= max_files):
        total_remaining = max(min_files - total_created, 1)
        max_size = int(total_size / total_remaining)
        if max_size < 2:
            break
        current_file_size = total_size if (max_files - total_created==1) else random.randrange(1, max_size)
        current_file_name = ''.join(random.choice(string.ascii_lowercase) for i in range(random.randrange(4, 10)))
        current_file_path = "{directory}/{file_name}".format(directory=dest, file_name=current_file_name)
        rc = create_binary_file(int(current_file_size), current_file_path)
        total_created += (1 + rc)
        total_size -= (current_file_size + (current_file_size*rc))
        print("Remaining size {}".format(to_si(int(total_size))))
        loop_breaker.append(total_size)
        # break loop if last 10 values have been consistently same, indicates problem creating files
        xor_result = 0
        for q_item in loop_breaker:
            xor_result ^= int(q_item)
        if xor_result == 0:
            print("Detected infinite loop. Breaking...")
            break
    return total_created

def is_unit_supported(unit: str) -> bool:
    return True if UNITS.index(unit) != -1 else False

def validate_size(size: str) -> bool:
    try: 
        _, unit = int(re.match(r'(\d+)(\w+)', size)[1]), re.match(r'(\d+)(\w+)', size)[2]
        if not is_unit_supported(unit):
            raise ValueError
    except:
        raise ValueError
    return size

def scan(dest: str) -> (int, int):
    files = [os.path.join(dest, f) for f in os.listdir(dest) if os.path.isfile(os.path.join(dest, f))]
    size = sum(os.path.getsize(f) for f in files)
    return size, len(files)

def in_bytes(number: int, unit: str) -> int:
    base = 1000
    exponent = UNITS.index(unit) if UNITS.index(unit) != -1 else 1
    return math.pow(base, exponent) * number

def to_si(number: int) -> str:
    base = 1000
    if number < base:
        return "{} bytes".format(number)
    div, exp = base, 1
    n = number / base
    while n >= base:
        div *= base
        exp += 1
        n /= base
    return "{:.2f} {}".format(number/div, UNITS[exp])

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--size", help="total size of random data in supported units: {}".format(','.join(UNITS)), type=validate_size, required=True)
    parser.add_argument("--max-files", help="maximum number of files to create", type=int, required=True)
    parser.add_argument("--min-files", help="minimum number of files to create", default=1, type=int)
    parser.add_argument("--dest-dir", help="destination directory", type=str, required=True)
    args = parser.parse_args()
    size, unit =  re.match(r'(\d+)(\w+)', args.size)[1], re.match(r'(\d+)(\w+)', args.size)[2]
    size_in_bytes = in_bytes(int(size), unit)
    occupied_size, occupied_files = scan(args.dest_dir)
    new_min_files = max(0, args.min_files - occupied_files)
    new_max_files = max(0, args.max_files - occupied_files)
    new_size = max(0, size_in_bytes-occupied_size)
    print("Destination directory contains {} files of {} size".format(occupied_files, to_si(occupied_size)))
    created = create_random_files(new_size, new_min_files, new_max_files, args.dest_dir)
    print("Created {} random files".format(created))

