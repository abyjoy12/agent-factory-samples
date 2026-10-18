"""Small, bounded application workloads with real process and health evidence."""
import ctypes
import hashlib
import json
import logging
import logging.handlers
import os
import random
import time
import urllib.request
from http.server import BaseHTTPRequestHandler, HTTPServer
from pathlib import Path

STATE = Path('/run/lab')
DATA = Path('/var/lib/operations')
APPLICATIONS = {
    'orders-api': dict(role='Order lookup and request processing', port=8081, cache_mib=6),
    'inventory-api': dict(role='Inventory availability lookup', port=8082, cache_mib=4),
    'job-worker': dict(role='Background order reconciliation', cache_mib=8),
    'report-cron': dict(role='Periodic operations summaries', cache_mib=4),
    'log-forwarder': dict(role='Application activity logging', cache_mib=2),
}


def process_name(name):
    # Linux comm is limited to 15 characters. Keep names identical in osquery.
    ctypes.CDLL(None).prctl(15, name.encode()[:15], 0, 0, 0)


def write_status(name, count, started, duration=0):
    status = dict(name=name, pid=os.getpid(), completed=count, started_at=started,
                  updated_at=time.time(), last_work_ms=round(duration * 1000, 2))
    temp = STATE / (name + '.tmp')
    temp.write_text(json.dumps(status))
    temp.replace(STATE / (name + '.json'))
    return status


def serve(name, stop):
    config = APPLICATIONS[name]
    process_name(name)
    os.nice(10)
    # Fixed, touched caches; no accumulating allocations or unbounded queues.
    cache = bytearray(b'x') * (config['cache_mib'] * 1024**2)
    started, count = time.time(), 0
    STATE.mkdir(exist_ok=True, parents=True)
    DATA.mkdir(exist_ok=True, parents=True)
    logger = None
    if name == 'log-forwarder':
        logger = logging.getLogger(name)
        logger.setLevel(logging.INFO)
        logger.addHandler(logging.handlers.RotatingFileHandler(
            DATA / 'application.log', maxBytes=256 * 1024, backupCount=2))
    if 'port' in config:
        class Handler(BaseHTTPRequestHandler):
            def do_GET(self):
                nonlocal count
                count += 1
                body = json.dumps(dict(service=name, status='up', requests=count,
                                       uptime_seconds=round(time.time() - started, 1))).encode()
                self.send_response(200 if self.path in ('/health', '/status') else 404)
                self.send_header('Content-Type', 'application/json')
                self.send_header('Content-Length', str(len(body)))
                self.end_headers()
                self.wfile.write(body)

            def log_message(self, *_):
                pass

        class Server(HTTPServer):
            allow_reuse_address = True

        with Server(('127.0.0.1', config['port']), Handler) as http:
            http.timeout = 0.5
            while not stop.is_set():
                http.handle_request()
                write_status(name, count, started)
        return
    count = 0
    while not stop.is_set():
        tick = time.monotonic()
        # Random timing and small CPU bursts keep observations varied and cheap.
        deadline = tick + random.uniform(0.002, 0.008)
        while time.monotonic() < deadline:
            hashlib.sha256(memoryview(cache)[:4096]).digest()
        count += random.randint(1, 4)
        if name == 'job-worker':
            for port in (8081, 8082):
                try:
                    with urllib.request.urlopen(f'http://127.0.0.1:{port}/status', timeout=0.5) as reply:
                        reply.read(1024)
                except OSError:
                    pass
        elif name == 'report-cron':
            report = dict(generated_at=time.time(), orders_reviewed=count,
                          inventory_checks=count * 2, pending_reviews=random.randint(0, 8))
            (DATA / 'latest-report.json').write_text(json.dumps(report))
        elif logger:
            logger.info('event=%s processed=%d time=%.3f',
                        random.choice(('order_checked', 'stock_checked', 'report_ready')), count, time.time())
        write_status(name, count, started, time.monotonic() - tick)
        stop.wait(random.uniform(5, 10) if name == 'report-cron' else random.uniform(0.8, 2.5))
