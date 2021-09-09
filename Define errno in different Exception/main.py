# import os
# import subprocess
# import sys
#
# s = subprocess.Popen(fr'C:\Users\flynn.chen\python_tws\python.exe test1.py',
#                      cwd=os.getcwd(),
#                      stdout=subprocess.PIPE,
#                      stderr=subprocess.PIPE,
#                      errors='ignore',
#                      text=True
#                      )
# out, err = s.communicate()
# if out:
#     print(1)
# if err:
#     raise RuntimeError(err)

import os
import subprocess
import sys

try:
    s = subprocess.run(fr'python sub.py',
                       cwd=os.getcwd(),
                       check=True,
                       capture_output=True,
                       text=True,
                       errors='ignore'
                       )
except subprocess.CalledProcessError as e:
    print(e.returncode)
    print(e.cmd)
    print(e.stdout)
    print(e.stderr)