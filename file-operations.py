#!/usr/bin/env python

import os
import re
import math
import time
import stat
import string
import random
import argparse
from enum import Enum
from os.path import isfile, join
from threading import Thread, Lock


UNITS = ["b", "Ki", "Mi", "Gi", "Ti"]

# when following file is present in the 
# directory, file operations will be paused
PAUSE_SWITCH = "__pause__"

class c:
    OKGREEN = '\033[92m'
    WARNING = '\033[93m'
    FAIL = '\033[91m'
    ENDC = '\033[0m'

def ok(msg: str):
    print("{}{}{}".format(c.OKGREEN, msg, c.ENDC))

def warn(msg: str):
    print("{}{}{}".format(c.WARNING, msg, c.ENDC))

def err(msg: str):
    print("{}{}{}".format(c.FAIL, msg, c.ENDC))

class FileOperations(object):
    def __init__(self, dest_dir, buffer):
        self.mutex = Lock()
        self.altered_bytes = 0
        self.buffer = buffer
        self.dir = dest_dir
        self.files = {}

    def scan(self):
        """ scans self.dir to create list of files """
        ok("Scanning directory {}".format(self.dir))
        try:
            self.files = {}
            self.mutex.acquire()
            for f in os.listdir(self.dir):
                if isfile(join(self.dir, f)):
                    self.files[join(self.dir, f)] = True
        finally:
            self.mutex.release()

    def update_altered_bytes(self, delta):
        try:
            self.mutex.acquire()
            self.altered_bytes += delta
        finally:
            self.mutex.release()

    def _get_file_list(self) -> dict:
        files = {}
        try:
            self.mutex.acquire()
            files = self.files
        finally:
            self.mutex.release()
        return files

    def _delete_from_file_list(self, path: str):
        try:
            self.mutex.acquire()
            del self.files[path]
        finally:
            self.mutex.release()
    
    def _add_to_file_list(self, path: str):
        try:
            self.mutex.acquire()
            self.files[path] = True
        finally:
            self.mutex.release()
        
    def _get_random_operation(self):
        return random.randint(1, 6)

    def perform_random_operation(self) -> int:
        if len(self._get_file_list().keys()) < 1:
            warn("Directory is empty or not scanned")
            return -1
        if join(self.dir, PAUSE_SWITCH) in self._get_file_list():
            warn("Pause switch present in the directory. Pausing until it's removed...")
            return 0
        return self._perform(self._get_random_operation())

    def _perform(self, opcode: int) -> int:
        path = random.choice(list(self._get_file_list().keys()))
        return {
            '1': self._read,
            '2': self._write,
            '3': self._append,
            '4': self._delete,
            '5': self._wipe,
            '6': self._chmod,
        }[str(opcode)](path)

    def _read(self, path) -> int:
        """ reads bytes from file """
        try:
            with open(path, 'rb') as f:
                f.read()
            ok("Read file {}".format(path))
        except FileNotFoundError:
            self._delete_from_file_list(path)
            return -1
        except Exception as e:
            err("Failed reading {} {}".format(path, str(e)))
            return -1
        return 0

    def _write_to_file(self, data: bytes, path: str, mode: str) -> int:
        try:
            with open(path, mode) as f:
                f.write(data)
        except Exception as e:
            err("Failed writing to file {} {}".format(path, str(e)))
            return -1
        return 0

    def _generate_random_bytes(self, size: int) -> bytes:
        generated_size = 0
        data = b''
        while generated_size < size:
            generated_size = random.randint(min(size-generated_size, 10), size-generated_size)
            data += os.urandom(generated_size) + bytes("\n", encoding='utf8')
            generated_size += generated_size
        return data

    def _write(self, path) -> int:
        """ writes a new file """
        if (self.buffer - self.altered_bytes) < 2:
            return 0
        size = random.randint(1, self.buffer - self.altered_bytes)
        file_name = ''.join(random.choice(string.ascii_lowercase) for i in range(random.randrange(10, 20)))
        path = join(self.dir, file_name)
        data = self._generate_random_bytes(size)
        rc = self._write_to_file(data, path, "wb+")
        self.update_altered_bytes((1+rc)*size)
        self._add_to_file_list(path)
        if rc == 0:
            ok("Created new file {} of size {}".format(path, to_si(size)))
        return rc

    def _append(self, path) -> int:
        """ appends random bytes to an existing file """
        if (self.buffer - self.altered_bytes) < 2:
            return 0
        size = random.randint(1, self.buffer - self.altered_bytes)
        data = self._generate_random_bytes(size)
        rc = self._write_to_file(data, path, "ab+")
        self.update_altered_bytes((1+rc)*size)
        self._add_to_file_list(path)
        if rc == 0:
            ok("Appended {} of data to {}".format(to_si(size), path))
        return rc

    def _delete(self, path) -> int:
        """ deletes a file """
        if PAUSE_SWITCH in path:
            return 0
        try:
            size = os.path.getsize(path)
            os.remove(path)
            self.update_altered_bytes(-1*size)
            self._delete_from_file_list(path)
            ok("Deleted file {}".format(path))
        except Exception as e:
            err("Failed deleting file {} {}".format(path, str(e)))
            return -1
        return 0

    def _wipe(self, path) -> int:
        """ deletes random bytes from a file """
        if os.path.getsize(path) < 2:
            return 0
        size = random.randint(1, os.path.getsize(path))
        try:
            file_name = join(self.dir, ''.join(random.choice(string.ascii_lowercase) for i in range(random.randrange(10, 20))))
            with open(path, 'rb') as in_file:
                with open(file_name, 'wb') as out_file:
                    out_file.write(in_file.read()[size:])
            os.replace(file_name, path)
            self.update_altered_bytes(-1*size)
            ok("Deleted {} bytes from {}".format(size, path))
        except Exception as e:
            err("Failed deleting bytes from file {} {}".format(path, e))
            return -1
        return 0

    def _chmod(self, path) -> int:
        """ randomizes file permissions """
        perms = [
            stat.S_IXUSR, 
            stat.S_IRGRP, stat.S_IWGRP, stat.S_IXGRP,
            stat.S_IROTH, stat.S_IWOTH, stat.S_IXOTH
        ]
        target_perm = stat.S_IWUSR | stat.S_IRUSR
        for _ in range(0, random.randint(1, len(perms))):
            target_perm |= random.choice(perms)
        try:
            os.chmod(path, target_perm)
            ok("Changed permissions of file {} to {}".format(path, str(target_perm)))
        except Exception as e:
            err("Failed changing permissions on file {} {}".format(path, str(e)))
            return -1
        return 0

def is_destination_valid(dest_dir: str) -> bool:
    if not os.path.exists(dest_dir):
        raise ValueError("Destination directory does not exist")
    if not os.path.isdir(dest_dir):
        raise ValueError("Destination is not a directory")
    return dest_dir

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

def is_unit_supported(unit: str) -> bool:
    return True if UNITS.index(unit) != -1 else False

def scanner(fileOps: FileOperations):
    while True:
        time.sleep(30)
        ok("[Scanner] Scanning destination directory")
        fileOps.scan()

def operator(fileOps: FileOperations):
    currentExp = 0
    while True:
        time.sleep(random.randint(1, 4))
        rc = fileOps.perform_random_operation()
        if rc != 0:
            time.sleep(math.pow(2, currentExp))
            currentExp += 1
        else:
            currentExp /= 2

def is_si_size_valid(size: str) -> bool:
    try: 
        _, unit = int(re.match(r'(\d+)(\w+)', size)[1]), re.match(r'(\d+)(\w+)', size)[2]
        if not is_unit_supported(unit):
            raise ValueError
    except:
        raise ValueError
    return size

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--dest-dir", help="destination directory", type=is_destination_valid, required=True)
    parser.add_argument("--buffer", help="extra wiggle room for file operations in supported units [{}]".format(','.join(UNITS)), type=is_si_size_valid, default='1b')
    args = parser.parse_args()
    size, unit =  re.match(r'(\d+)(\w+)', args.buffer)[1], re.match(r'(\d+)(\w+)', args.buffer)[2]
    operations = FileOperations(args.dest_dir, in_bytes(int(size), unit))
    scannerThread = Thread(target=scanner, args=(operations,))
    operatorThread = Thread(target=operator, args=(operations,))
    scannerThread.start()
    operatorThread.start()
    scannerThread.join()
    operatorThread.join()
