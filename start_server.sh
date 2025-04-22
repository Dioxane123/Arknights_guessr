#!/bin/bash
cd /var/www/flaskapp
source /home/$(whoami)/guessr/bin/activate
gunicorn --worker-class eventlet -w 1 -b 0.0.0.0:12920 app:app
