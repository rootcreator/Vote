# gunicorn_config.py
bind = "0.0.0.0:8000"
workers = 3  # Adjust based on your system's resources
timeout = 120
