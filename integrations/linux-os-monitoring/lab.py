"""Operator-only fault controls and supervised demo workloads. Not an MCP tool."""
import argparse
import fcntl
import json
import os
import subprocess
import sys
import threading
import time
from pathlib import Path

from applications import APPLICATIONS, process_name, serve

STATE = Path('/run/lab')
DATA = Path('/var/lib/operations')
SCENARIOS = ('normal', 'cpu', 'memory', 'disk', 'service-down')


def set_scenario(name, seconds=180):
    if name not in SCENARIOS or not 10 <= seconds <= 300:
        raise ValueError('Unknown scenario or duration outside 10–300 seconds')
    STATE.mkdir(exist_ok=True, parents=True)
    with (STATE / 'operator.lock').open('w') as lock:
        fcntl.flock(lock, fcntl.LOCK_EX)
        temp = STATE / 'scenario.tmp'
        temp.write_text(json.dumps(dict(name=name, expires_at=time.time() + seconds,
                                       generation=time.time_ns())))
        temp.replace(STATE / 'scenario.json')


def worker(name):
    # Distinct process names appear in osquery; no artificial telemetry is injected.
    if name in APPLICATIONS:
        serve(name, threading.Event())
        return
    process_name({'cpu': 'batch-indexer', 'memory': 'cache-builder'}[name])
    os.nice(15)
    if name == 'cpu':
        while True:
            end = time.monotonic() + 0.08
            while time.monotonic() < end:
                pass
            time.sleep(0.02)
    if name == 'memory':
        blocks = []
        for _ in range(72):  # 1,152 MiB plus service overhead reliably crosses 75%.
            blocks.append(bytearray(b'\x01') * (16 * 1024 * 1024))
            time.sleep(0.2)
        while True:
            time.sleep(1)

def spawn(name):
    return subprocess.Popen([sys.executable, str(Path(__file__).resolve()), '_worker', name])


def terminate(process):
    if process and process.poll() is None:
        process.terminate()
        try:
            process.wait(timeout=3)
        except subprocess.TimeoutExpired:
            process.kill()
            process.wait()


def supervise(stop):
    children, fault, active = {}, None, None
    fault_file = DATA / 'scenario-fill.bin'
    try:
        while not stop.is_set():
            try:
                config = json.loads((STATE / 'scenario.json').read_text())
                if config['name'] not in SCENARIOS or time.time() >= config['expires_at']:
                    config = {'name': 'normal', 'generation': 0}
            except (OSError, ValueError, KeyError):
                config = {'name': 'normal', 'generation': 0}
            key = (config['name'], config['generation'])
            if key != active:
                terminate(fault)
                fault = None
                fault_file.unlink(missing_ok=True)
                if config['name'] in ('cpu', 'memory'):
                    fault = spawn(config['name'])
                elif config['name'] == 'disk':
                    # Write real blocks, not a sparse file, on the bounded demo tmpfs.
                    with fault_file.open('wb') as stream:
                        for _ in range(58):
                            stream.write(b'\0' * (1024 * 1024))
                active = key
            for name in APPLICATIONS:
                process = children.get(name)
                if name == 'orders-api' and config['name'] == 'service-down':
                    terminate(process)
                    children[name] = None
                elif process is None or process.poll() is not None:
                    children[name] = spawn(name)
            service = children.get('orders-api')
            status = dict(scenario=config['name'], generation=config['generation'],
                          expires_at=config.get('expires_at'), service_pid=service.pid if service else None,
                          fault_pid=fault.pid if fault and fault.poll() is None else None,
                          fault_exited=fault is not None and fault.poll() is not None,
                          application_pids={name: p.pid if p else None for name, p in children.items()},
                          updated_at=time.time())
            temp = STATE / 'status.tmp'
            temp.write_text(json.dumps(status))
            temp.replace(STATE / 'status.json')
            stop.wait(0.5)
    finally:
        terminate(fault)
        for process in children.values():
            terminate(process)
        fault_file.unlink(missing_ok=True)


def main():
    if len(sys.argv) == 3 and sys.argv[1] == '_worker':
        worker(sys.argv[2])
        return
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('scenario', choices=(*SCENARIOS, 'reset', 'status'))
    parser.add_argument('--seconds', type=int, default=180)
    args = parser.parse_args()
    if args.scenario == 'status':
        print((STATE / 'status.json').read_text())
    else:
        set_scenario('normal' if args.scenario == 'reset' else args.scenario, args.seconds)
        print('Requested', args.scenario, '(automatically resets after at most', args.seconds, 'seconds)')


if __name__ == '__main__':
    main()
