import argparse
import os
import re
import sys
import time
import subprocess
import numpy as np
import json
import multiprocessing

current_dir = os.getcwd()
print(current_dir)
CPU = 96 # no of simultaneous runs.

def parallize_jobs(jobs):
    if jobs:
        procs = multiprocessing.Pool(CPU)
        procs.map(get_sequences, jobs)
        procs.close()
        procs.join()

def get_sequences(data):
    outfname = "ncbi_idx_%s.fasta"%(data)
    command2= ["curl", "-s", "https://data.orthodb.org/current/fasta?id=%s&species="%(data), "-L", '-o', outfname]
    print(" ".join(command2))
    response2 = subprocess.Popen(command2)
    out2, err2 = response2.communicate(timeout=5)

def map_retrieve(ncbi_id=None, w_dir=None):
    print("WORKING ON %s" % ncbi_id)
    out_dir_name="ncbi_id_%s_sequences"%ncbi_id
    d_dir = os.path.join(w_dir, out_dir_name)

    # create a output directory for each ncbi_id
    if not os.path.exists(d_dir):
        os.mkdir(d_dir)
    else:
        pass

    os.chdir(d_dir)
    # command1 = ["curl", "https://data.orthodb.org/current/search?level=%s&species=%s&limit=10000000"%(ncbi_id, ncbi_id)] # by default only 1000 ids can be downloaded, limit=10000000 is set to overcome it.
    command1 = ["curl", "https://data.orthodb.org/current/search?universal=0.9&singlecopy=0.9&level=%s&species=%s&take=5000"%(ncbi_id, ncbi_id)]

    print(" ".join(command1))
    response = subprocess.Popen(command1, stdout=subprocess.PIPE) # pipe the terminal output to response
    out, err = response.communicate(timeout=5) # Wait for process to terminate
    p_status = response.wait() # Wait for child process to terminate. Additional wait time, just in case there is a lag.
    out = json.loads(out) # convert the output from bytes to dictionary

    if out:
        #print(out)
        groups  = out["data"]
        print(len(groups))
        parallize_jobs(groups) # parallize the fasta download.

    os.chdir(w_dir)


# put in you ncbi_ids here. Can do multiple ids in a single go.
ncbi_ids = [4827]
for id in ncbi_ids:
    map_retrieve(ncbi_id=id, w_dir=current_dir)
