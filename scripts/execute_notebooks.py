from __future__ import annotations
from pathlib import Path
import nbformat
from nbclient import NotebookClient
ROOT=Path(__file__).resolve().parents[1]
for name in ['House_Price_Prediction_Detailed.ipynb','House_Price_Prediction_Basic.ipynb']:
    path=ROOT/'notebooks'/name; nb=nbformat.read(path,as_version=4)
    client=NotebookClient(nb,timeout=600,kernel_name='python3',resources={'metadata':{'path':str(ROOT)}})
    client.execute(); nbformat.write(nb,path)
    errors=[o for c in nb.cells if c.cell_type=='code' for o in c.get('outputs',[]) if o.get('output_type')=='error']
    if errors: raise RuntimeError(f'{name} co cell error')
    print('NOTEBOOK_PASS',name,'cells',len(nb.cells))
