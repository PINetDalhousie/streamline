import subprocess
import sys
import os
os.mkdir("pyflink")
subprocess.check_call([sys.executable, '-m', 'pip', 'install', '--target', 'pyflink', 'apache-flink==1.17.1'])

