"""Container-scoped evidence. No caller-supplied SQL, commands or filesystem paths."""
from __future__ import annotations

import json
import os
import re
import shutil
import socket
import sqlite3
import subprocess
import threading
import time
import urllib.request
from datetime import datetime, timezone
from pathlib import Path

from applications import APPLICATIONS

QUERIES = {
    'os': 'SELECT name, version, platform, arch FROM os_version LIMIT 1;',
    'processes': ('SELECT pid, parent, name, path, resident_size, user_time, system_time, '
                  'start_time FROM processes ORDER BY resident_size DESC LIMIT 80;'),
    'listeners': ('SELECT pid, port, protocol, address FROM listening_ports '
                  'WHERE port IN (8000,8081,8082) LIMIT 20;'),
}
SCOPE = 'Linux machine linux-ops-01: assigned resources, visible processes and configured application checks.'


def utc():
    return datetime.now(timezone.utc).isoformat(timespec='milliseconds')


class Cgroups:
    """Resolve v1 controller mounts and v2 unified mounts, including namespace roots."""
    def __init__(self, proc=Path('/proc'), root=Path('/')):
        self.paths = {}
        entries = []
        for line in (proc / 'self/cgroup').read_text().splitlines():
            _, controllers, path = line.split(':', 2)
            entries.append((controllers.split(','), path))
        for line in (proc / 'self/mountinfo').read_text().splitlines():
            before, after = line.split(' - ', 1)
            fields, fs = before.split(), after.split()
            if fs[0] not in ('cgroup', 'cgroup2'):
                continue
            mount_root, mount_point = fields[3:5]
            for controllers, path in entries:
                names = ['unified'] if fs[0] == 'cgroup2' and controllers == [''] else controllers
                if fs[0] == 'cgroup' and not set(names).intersection(fs[2].split(',')):
                    continue
                # A private cgroup namespace reports '/' at its delegated mount root.
                if path == '/':
                    relative = ''
                elif mount_root == '/':
                    relative = path.lstrip('/')
                elif path == mount_root or path.startswith(mount_root.rstrip('/') + '/'):
                    relative = path[len(mount_root):].lstrip('/')
                else:
                    continue
                for name in names:
                    self.paths[name] = root / mount_point.lstrip('/') / relative
        if not self.paths:
            raise RuntimeError('Container cgroup mounts could not be resolved')

    def read(self, controller, name):
        base = self.paths.get('unified', self.paths.get(controller))
        if base is None:
            raise RuntimeError(f'Missing {controller} cgroup controller')
        return (base / name).read_text().strip()

    def counters(self):
        v2 = 'unified' in self.paths
        memory = int(self.read('memory', 'memory.current' if v2 else 'memory.usage_in_bytes'))
        limit = self.read('memory', 'memory.max' if v2 else 'memory.limit_in_bytes')
        limit = None if limit == 'max' or int(limit) >= 2**60 else int(limit)
        if v2:
            stat = dict(line.split() for line in self.read('cpu', 'cpu.stat').splitlines())
            cpu_ns = int(stat['usage_usec']) * 1000
            quota, period = self.read('cpu', 'cpu.max').split()
        else:
            cpu_ns = int(self.read('cpuacct', 'cpuacct.usage'))
            quota, period = self.read('cpu', 'cpu.cfs_quota_us'), self.read('cpu', 'cpu.cfs_period_us')
        affinity = len(os.sched_getaffinity(0))
        cpu_limit = affinity if quota == 'max' or int(quota) < 0 else min(affinity, int(quota) / int(period))
        if cpu_limit <= 0:
            raise RuntimeError('Invalid cgroup CPU quota')
        pids_max = self.read('pids', 'pids.max')
        return dict(memory_bytes=memory, memory_limit_bytes=limit, cpu_ns=cpu_ns,
                    cpu_limit_cores=cpu_limit, pids=int(self.read('pids', 'pids.current')),
                    pids_limit=None if pids_max == 'max' else int(pids_max), cgroup_version=2 if v2 else 1)


def resource_delta(first, second, elapsed):
    if elapsed <= 0 or second['cpu_ns'] < first['cpu_ns']:
        raise RuntimeError('CPU counters reset or measurement interval invalid; retry')
    cores = (second['cpu_ns'] - first['cpu_ns']) / 1e9 / elapsed
    result = dict(second)
    result.pop('cpu_ns')
    result.pop('cgroup_version', None)
    result.update(cpu_used_cores=round(cores, 3),
                  cpu_percent_of_limit=round(cores / second['cpu_limit_cores'] * 100, 1),
                  measurement_seconds=round(elapsed, 3), observed_at=utc(), scope=SCOPE)
    limit = second['memory_limit_bytes']
    result['memory_percent_of_limit'] = round(second['memory_bytes'] / limit * 100, 1) if limit else None
    result['pressure'] = [name for name, value, threshold in (
        ('cpu', result['cpu_percent_of_limit'], 75),
        ('memory', result['memory_percent_of_limit'], 75)) if value is not None and value >= threshold]
    result['notes'] = ['CPU includes monitoring overhead; memory includes charged cache and tmpfs. '
                       'Pressure thresholds are advisory, not service-level objectives.']
    return result


class Monitor:
    def __init__(self, state=Path('/run/lab'), data=Path('/var/lib/operations'), cgroups=None):
        self.state, self.data = state, data
        self.cgroups = cgroups or Cgroups()
        self.query_lock = threading.BoundedSemaphore(1)
        self.db_lock = threading.Lock()
        state.mkdir(parents=True, exist_ok=True)
        self.db = sqlite3.connect(state / 'history.sqlite', check_same_thread=False)
        self.db.execute('CREATE TABLE IF NOT EXISTS samples (ts REAL PRIMARY KEY, value TEXT NOT NULL)')
        self.db.commit()
        self.last_sample = None
        self.last_sample_ok = False

    def query(self, key):
        sql = QUERIES[key]  # Only fixed keys, never text from an MCP caller.
        if not self.query_lock.acquire(timeout=10):
            raise RuntimeError('osquery is busy; retry shortly')
        try:
            run = subprocess.run(['osqueryi', '--json', '--disable_extensions', '--disable_events', sql],
                                 capture_output=True, text=True, timeout=8, check=True)
            rows = json.loads(run.stdout)
            if not isinstance(rows, list):
                raise RuntimeError('Unexpected osquery result')
            return rows
        finally:
            self.query_lock.release()

    def resources(self, window=1.0):
        if not 0.25 <= window <= 3:
            raise ValueError('Measurement window must be 0.25–3 seconds')
        first, start = self.cgroups.counters(), time.monotonic()
        time.sleep(window)
        return resource_delta(first, self.cgroups.counters(), time.monotonic() - start)

    def filesystem(self):
        st = os.statvfs(self.data)
        total, available = st.f_blocks * st.f_frsize, st.f_bavail * st.f_frsize
        percent = round((total - available) / total * 100, 1) if total else None
        return dict(observed_at=utc(), scope='Operations data filesystem on linux-ops-01',
                    filesystem='tmpfs', mount=str(self.data), capacity_bytes=total,
                    available_bytes=available, used_percent=percent,
                    inodes=st.f_files, available_inodes=st.f_favail,
                    pressure=percent is not None and percent >= 85,
                    note='This measurement covers the configured RAM-backed operations filesystem only.')

    def overview(self):
        rows = self.query('os')
        if not rows:
            raise RuntimeError('osquery returned no OS identity')
        return dict(observed_at=utc(), scope=SCOPE, hostname=socket.gethostname(),
                    os=rows[0], osquery_version=subprocess.run(['osqueryi', '--version'],
                    capture_output=True, text=True, timeout=8, check=True).stdout.strip(),
                    resources=self.resources(), filesystem=self.filesystem(),
                    history=self.history(1)['coverage'])

    def top_processes(self, limit=5):
        if isinstance(limit, bool) or not isinstance(limit, int) or not 1 <= limit <= 10:
            raise ValueError('limit must be an integer between 1 and 10')
        before = {(r['pid'], r['start_time']): r for r in self.query('processes')}
        start = time.monotonic()
        time.sleep(1)
        after = self.query('processes')
        elapsed = time.monotonic() - start
        quota = self.cgroups.counters()['cpu_limit_cores']
        for row in after:
            old = before.get((row['pid'], row['start_time']))
            ms = sum(int(row[k]) - int(old[k]) for k in ('user_time', 'system_time')) if old else None
            row['cpu_percent_of_limit'] = round(ms / 1000 / elapsed / quota * 100, 1) if ms is not None and ms >= 0 else None
            row['resident_size_bytes'] = int(row.pop('resident_size'))
            for key in ('user_time', 'system_time'):
                row.pop(key)
        return dict(observed_at=utc(), scope=SCOPE, measurement_seconds=round(elapsed, 3),
                    by_cpu=sorted(after, key=lambda r: r['cpu_percent_of_limit'] or 0, reverse=True)[:limit],
                    by_memory=sorted(after, key=lambda r: r['resident_size_bytes'], reverse=True)[:limit],
                    note='Up to 80 processes sampled by RSS. New/reused PIDs have unknown CPU; '
                         'process intervals are approximate and include osquery overhead. No command arguments or environment values exposed.')

    def services(self):
        processes = {str(row['pid']): row for row in self.query('processes')}
        applications = []
        for name, config in APPLICATIONS.items():
            item = dict(name=name, role=config['role'])
            try:
                status = json.loads((self.state / (name + '.json')).read_text())
                age = time.time() - status['updated_at']
                process = processes.get(str(status['pid']))
                running = bool(process and process['name'] == name and 0 <= age < 20)
                item.update(pid=status['pid'] if running else None, status='running' if running else 'unavailable',
                            heartbeat_age_seconds=round(age, 1), completed=status['completed'],
                            last_work_ms=status['last_work_ms'])
            except (OSError, ValueError, KeyError):
                item.update(pid=None, status='unknown')
            if 'port' in config:
                try:
                    with urllib.request.urlopen(f"http://127.0.0.1:{config['port']}/health", timeout=2) as reply:
                        healthy = reply.status == 200
                        details = json.loads(reply.read(2048))
                    item.update(requests=details['requests'], uptime_seconds=details['uptime_seconds'])
                except (OSError, ValueError, KeyError):
                    healthy = False
                item.update(expected_port=config['port'], reachable=healthy, status='up' if healthy else 'down')
            applications.append(item)
        return dict(observed_at=utc(), scope=SCOPE, applications=applications,
                    listeners=self.query('listeners'),
                    note='Only the listed applications, their recent heartbeats, HTTP health checks '
                         'and ports 8000/8081/8082 were checked. This is not a full network availability test.')

    def record(self, value, now=None):
        now = time.time() if now is None else now
        with self.db_lock:
            self.db.execute('INSERT OR REPLACE INTO samples VALUES (?,?)', (now, json.dumps(value)))
            self.db.execute('DELETE FROM samples WHERE ts < ?', (now - 1800,))
            self.db.execute('DELETE FROM samples WHERE ts NOT IN (SELECT ts FROM samples ORDER BY ts DESC LIMIT 181)')
            self.db.commit()
        self.last_sample = now
        self.last_sample_ok = "error" not in value

    def history(self, minutes=5):
        if isinstance(minutes, bool) or not isinstance(minutes, int) or not 1 <= minutes <= 30:
            raise ValueError('minutes must be an integer between 1 and 30')
        now = time.time()
        with self.db_lock:
            rows = self.db.execute('SELECT ts,value FROM samples WHERE ts >= ? ORDER BY ts',
                                   (now - minutes * 60,)).fetchall()
        return dict(observed_at=utc(), scope=SCOPE, requested_minutes=minutes,
                    coverage=dict(samples=len(rows), cadence_seconds=10, retention_seconds=1800,
                                  first_sample_at=datetime.fromtimestamp(rows[0][0], timezone.utc).isoformat() if rows else None,
                                  latest_age_seconds=round(now - rows[-1][0], 1) if rows else None,
                                  covered_seconds=round(rows[-1][0] - rows[0][0], 1) if rows else 0),
                    samples=[json.loads(row[1]) for row in rows],
                    note='Observed history only; gaps/errors are not healthy samples. History resets when monitoring restarts.')

    def collect(self, stop):
        while not stop.is_set():
            started = time.monotonic()
            try:
                value = dict(resources=self.resources(), filesystem=self.filesystem())
            except Exception as exc:
                value = dict(observed_at=utc(), error=type(exc).__name__ + ': ' + str(exc))
            self.record(value)
            stop.wait(max(0, 10 - (time.monotonic() - started)))
