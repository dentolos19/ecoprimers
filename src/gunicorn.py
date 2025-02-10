import os

from dotenv import load_dotenv

for env_file in (".env", "../.env"):
    env = os.path.join(os.getcwd(), env_file)
    if os.path.exists(env):
        load_dotenv(env)


loglevel = "info"
errorlog = "-"  # stderr
accesslog = "-"  # stdout
worker_tmp_dir = "/dev/shm"
graceful_timeout = 120
limit_request_field_size = 16384
timeout = 120
keepalive = 5
threads = 3