import os

bind = f"0.0.0.0:{os.environ.get('PORT', '8000')}"
workers = 2
forwarded_allow_ips = "*"
accesslog = "-"
errorlog = "-"
loglevel = "debug"
capture_output = True
