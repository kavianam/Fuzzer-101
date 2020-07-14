#!/usr/bin/python
import glob
import os
import subprocess
import threading
import random
import time

# Run one fuzz case with the provided input (which is a byte array)
def fuzz(thrd_id: int, inp: bytearray):
    assert isinstance(thrd_id, int)
    assert isinstance(inp, bytearray)


    tmpfn = f"tmpinput{thrd_id}"
    # Write out the input to a temporary file
    with open(tmpfn, "wb") as f:
        f.write(inp)

    # Run objdump until complation
    #p = subprocess.Popen(['objdump', '-d', tmpfn])
    p = subprocess.Popen(['./objdump', '-x', tmpfn],
                         stdout=subprocess.DEVNULL,
                         stderr=subprocess.DEVNULL)
    return_code = p.wait()

    # Assert that the program ran successfully
    #assert return_code >= 0
    if return_code != 0:
        print(f"Exited with {return_code} exit code")


# Get a listing of all the files in the corpus
# The corpus is the set of files which we pre-seeded the fuzzer with to give it valid inputs.
# These are files that the program should be able to handle parsing, that we will ultimately
# mutate to try to find bugs!
corpus_filenames = glob.glob('./corpus/*')

#file_names = glob.glob('./test/*')
corpus = set()

for file_name in corpus_filenames:
    with open(file_name, "rb") as f:
        corpus.add(f.read())

# Convert the corpus back into a list as we're done the set for deduping inputs which
# were not unique and convert bytes to bytearray because bytes are immutable and we
# want to change it, so we use bytearray that is mutable
corpus = list(map(bytearray, corpus))

# Get the time of the start of the fuzzer
start = time.time()

# Total number of fuzz cases
cases = 0


def worker(thrd_id):
    global corpus, start, cases
    # Shuffle to pick a random input from our corpus
    #random.shuffle(corpus)

    for i in range(10):
        # Create a copy of an existing input from the corpus
        inp = bytearray(random.choice(corpus))

        for _ in range(random.randint(1, 8)):
            inp[random.randint(0, len(inp))] = random.randint(0, 255)
        
        # Pick a random input from out corpus
        fuzz(thrd_id, inp)

        # Determine the amount of seconds we have been fuzzing
        elapsed = time.time() - start

        # Update the number of fuzz cases
        cases += 1

        # Determine the number of fuzz cases per second
        fcps = cases / elapsed

        print(f"[{elapsed:10.4f}] cases {cases:10} | fcps {fcps:10.4f}")


for i in range(10):
    threading.Thread(target=worker, args=(i,)).start()

#while threading.activeCount() > 1:
#    time.sleep(0.1)

