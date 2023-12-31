import os

# Restart Gunicorn every 950-1050 requests
# May mitigate memory leak attacks
max_requests = 1000
max_requests_jitter = 50

listening_address = os.environ.get("LISTENING_ADDRESS", "0.0.0.0")
listening_port = os.environ.get("LISTENING_PORT", "5000")
bind = "{}:{}".format(listening_address, listening_port)

# May thread starve /!\
workers = 1
timeout = 120
