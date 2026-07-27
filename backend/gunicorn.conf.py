# backend/gunicorn.conf.py
import multiprocessing

# 1. bind
bind = "127.0.0.1:8000"

# 2. Replaces: -w 5 (We use code to calculate the perfect number of workers automatically!)
# workers = (multiprocessing.cpu_count() * 2) + 1
workers = 2
# 3. Replaces: --access-logfile - (Prints your clicks to the terminal console)
access_logfile = "-"

# 4. Added Safety Valve: Protects your views from timing out too quickly
timeout = 60
