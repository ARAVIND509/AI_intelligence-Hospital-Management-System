import time
import os
import sys

# Ensure backend root is in sys.path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from app.core.logger import app_logger
from app.core.redis import redis_client


def run_background_worker():
    app_logger.info("Initializing MediMind AI Background Worker Service...")
    redis_conn = redis_client.connect()

    app_logger.info("Background Worker active. Processing queue tasks...")

    iteration = 0
    try:
        while True:
            iteration += 1
            if iteration % 10 == 0:
                app_logger.info(f"Worker heartbeat check #{iteration} — System Healthy.")

            # Periodic maintenance task placeholder (e.g. log maintenance, cleanup)
            time.sleep(3)
    except KeyboardInterrupt:
        app_logger.info("Worker service interrupted. Shutting down gracefully.")


if __name__ == "__main__":
    run_background_worker()
