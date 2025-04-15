import sys
import os
sys.path.insert(0, '/var/www/flaskapp')

python_version = f'python{sys.version_info.major}.{sys.version_info.minor}'
I = os.popen(whoami)
sys.path.insert(0, f'/home/{I.readlines()[0][:-1]}/guessr/bin')
I = os.popen(whoami)
sys.path.insert(0, f'/home/{I.readlines()[0][:-1]}/guessr/lib/{python_version}/site-packages')

project_dir = os.path.dirname(os.path.abspath(__file__))
os.chdir(project_dir)
if project_dir not in sys.path:
	sys.path.insert(0, project_dir)
from main import app as application
