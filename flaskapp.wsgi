# 当前版本改用Eventlet+Gunicorn处理并发场景，Apache2仅用作反向代理，理论上此文件已经没用了，在以后的版本中会删除.
import sys
import os
sys.path.insert(0, '/var/www/flaskapp')

python_version = f'python{sys.version_info.major}.{sys.version_info.minor}'
#I = os.popen("whoami")
#sys.path.insert(0, f'/home/{I.readlines()[0][:-1]}/guessr/bin')
#I = os.popen("whoami")
#sys.path.insert(0, f'/home/{I.readlines()[0][:-1]}/guessr/lib/{python_version}/site-packages')
sys.path.insert(0, f'/home/{your-user-name}/guessr/bin')
sys.path.insert(0, f'/home/{your-user-name}/guessr/lib/{python_version}/site-packages')

project_dir = os.path.dirname(os.path.abspath(__file__))
os.chdir(project_dir)
if project_dir not in sys.path:
	sys.path.insert(0, project_dir)
from app import app as application
