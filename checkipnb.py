#!/usr/bin/env python
"""
simple example script for running notebooks and reporting exceptions.

Usage: `checkipnb.py foo.ipynb [bar.ipynb [...]]`

Each cell is submitted to the kernel, and checked for errors.
"""

import os,sys,time

from Queue import Empty

from jupyter_client import KernelManager

from nbformat import read, reads, NotebookNode

def run_notebook(nb, ipynb):
    max_time = 100 # maximum time for each cell
    km = KernelManager()
    km.start_kernel(stderr=open(os.devnull, 'w'))
    kc = km.client()
    # simple ping:
    kc.execute("pass")
    kc.get_shell_msg()

    cells = 0
    failures = 0
    for cell in nb.cells:
        if cell.cell_type != 'code':
            continue
        kc.execute(cell.source)
        try:
            reply = kc.get_shell_msg(timeout=max_time)['content']
            if reply['status'] == 'error':
                failures += 1
                print("\n\n************")
                print("FAILURE:")
                print("************\n")
                print(cell.source)
                print('-----')
                print("raised:")
                print('\n'.join(reply['traceback']))
                print("\n")
        except Exception:
            print("\n\n**************************************************")
            print("Cell timed out. Max time allowed per cell = {0}".format(max_time))
            print("**************************************************\n")
            print(cell.source)
            print("Skipping remaining cells")
            break
        cells += 1
        sys.stdout.write('.')
   
    print("\n\n****************************************")
    print("ran notebook {0}".format(ipynb))
    print("    ran {0} cells".format(cells))
    if failures:
        print("    {0} cells raised exceptions".format(failures))
    print("****************************************")
    
    kc.stop_channels()
    km.shutdown_kernel()
    del km

if __name__ == '__main__':
    for ipynb in sys.argv[1:]:
        print("running {0}".format(ipynb))
        nb = read(ipynb, as_version=4)
        #with open(ipynb) as f:
        #    nb = reads(f.read(), 'json')
        run_notebook(nb, ipynb)
