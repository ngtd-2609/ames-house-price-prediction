from __future__ import annotations
import argparse
import asyncio
from pathlib import Path
import sys
import nbformat
from nbclient import NotebookClient
from jupyter_client import KernelManager

if sys.platform == "win32" and hasattr(asyncio, "WindowsSelectorEventLoopPolicy"):
    asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())
ROOT=Path(__file__).resolve().parents[1]
parser=argparse.ArgumentParser()
parser.add_argument('--only',choices=('both','detailed','basic'),default='both')
args=parser.parse_args()
notebooks={
    'detailed':'House_Price_Prediction_Detailed.ipynb',
    'basic':'House_Price_Prediction_Basic.ipynb',
}
names=list(notebooks.values()) if args.only=='both' else [notebooks[args.only]]
for name in names:
    path=ROOT/'notebooks'/name; nb=nbformat.read(path,as_version=4)
    manager=KernelManager(kernel_name='python3')
    # Use this environment, even if a user-level python3 kernel points elsewhere.
    manager.kernel_spec.argv=[sys.executable,'-m','ipykernel_launcher','-f','{connection_file}']
    client=NotebookClient(nb,timeout=600,km=manager,resources={'metadata':{'path':str(ROOT)}})
    try:
        client.execute()
        nbformat.write(nb,path)
    finally:
        if manager.has_kernel:
            manager.shutdown_kernel(now=True)
    errors=[o for c in nb.cells if c.cell_type=='code' for o in c.get('outputs',[]) if o.get('output_type')=='error']
    if errors: raise RuntimeError(f'{name} co cell error')
    print('NOTEBOOK_PASS',name,'cells',len(nb.cells))
