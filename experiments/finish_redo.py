"""Wait for production and run dependent computational checks and reports."""
import json
from pathlib import Path
import subprocess
import sys
import time

run=Path(sys.argv[1])
while True:
    try:state=json.loads((run/'status.json').read_text())
    except (FileNotFoundError,json.JSONDecodeError):
        time.sleep(10);continue
    if state['status']=='complete':break
    if state['status'] in ('failed','error','superseded'):
        raise RuntimeError(f'Production stopped: {state}')
    time.sleep(10)
steps=['verify_redo','redo_report','redo_compare','redo_cross','redo_supplement','redo_stress_compare','redo_figures','redo_manuscript']
status={'completed':[],'status':'running'}
for step in steps:
    status['active']=step
    (run/'postprocessing_status.json').write_text(json.dumps(status,indent=2))
    print('POSTPROCESS',step,flush=True)
    try:subprocess.run([sys.executable,'-m','src.'+step,str(run)],check=True)
    except Exception as exc:
        status.update(status='failed',error=str(exc))
        (run/'postprocessing_status.json').write_text(json.dumps(status,indent=2))
        raise
    status['completed'].append(step)
status.update(status='complete',active=None)
(run/'postprocessing_status.json').write_text(json.dumps(status,indent=2))
