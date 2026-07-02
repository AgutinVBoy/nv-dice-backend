import os
import multiprocessing
from src.core.logger import get_log_config

bind = "0.0.0.0:8000"
workers = int(os.getenv("APP_WORKERS_COUNT", multiprocessing.cpu_count() * 2 + 1))
worker_class = "uvicorn.workers.UvicornWorker"

max_requests = 5000
max_requests_jitter = 100
timeout = 90

accesslog = "-"
errorlog = "-"

logconfig_dict = get_log_config()
