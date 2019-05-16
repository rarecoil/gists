#!/usr/bin/env python3
"""
maskify.py

Creates password categorization masks from big password lists
in a multithreaded fashion. Note that it assumes you have enough
RAM to hold the unique mask dict in memory. Used to analyze a 300M+
unique password list for types and occurrences. 

On an ODROID-C2, runs at about 50-52K passwords/sec.

Output file is mask like:

?l?l?l?l?l?d:n

where n is the number of occurrences of this mask.
"""

from multiprocessing import Pool, cpu_count
import re
import sys
import time

NUM_THREADS = cpu_count()
WORK_BLOCK_SIZE = 1024

LOWERCASE = "etaoinshrdlcumwfgypbvkjxqz" #?l
UPPERCASE = "ETAOINSHRDLCUMWFGYPBVKJXQZ" #?L
NUMBER    = "0123456789" #?d
PUNCT_1   = "~!@#$%^&*()_+" #?t
PUNCT_2   = "`[];',./-=\\ " #?c
PUNCT_3   = ":\"<>?|{}" #?C

PATTERNS = {
    "?l": LOWERCASE,
    "?L": UPPERCASE,
    "?d": NUMBER,
    "?t": PUNCT_1,
    "?c": PUNCT_2,
    "?C": PUNCT_3
}

def worker(line):
    """Make a pattern from a line or lines"""
    pat = ""
    patlen = 0
    for char in line:
        # uncomment the below block if you want to short circuit at a length of 16
        """
        if patlen == 16:
            break
        """
        for pattern_key in PATTERNS:
            if char in PATTERNS[pattern_key]:
                patlen += 1
                pat += str(pattern_key)
    return pat

if __name__ == '__main__':
    if len(sys.argv) != 3:
        print("Usage: maskify.py input_pwlist output_masklist")
        sys.exit(1)
    start = time.time()
    print("Utilising %d cores for processing." % NUM_THREADS)

    p = Pool(NUM_THREADS)
    u = dict()
    f = open(sys.argv[1], 'r')
    length_warn = False

    interval = 0
    checked = 0
    with p:
        patterns = p.imap_unordered(worker, f, WORK_BLOCK_SIZE)
        for pat in patterns:
            checked += 1

            if pat not in u:
                u[pat] = 1
            else:
                u[pat] += 1

            now = time.time()
            if interval == 0 or (interval + 5) < now:
                print("Processing. Speed: %f patterns/sec" % (checked / 5.0), end="\r")
                interval = now
                checked = 0
        
    
    print("\nSaving unique patterns to disk")
    with open(sys.argv[2], 'w') as g:
        for pattern in u:
            if pattern == '':
                continue
            g.write("%s:%d\n" % (pattern, u[pattern]))
    diff = time.time() - start
    print("Done. Took %f sec." % diff)
    sys.exit(0)