import json
import sys
import tempfile
import time
import unittest
from pathlib import Path
from unittest.mock import patch

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from monitoring import Cgroups, Monitor, QUERIES, resource_delta
import lab


class CgroupTests(unittest.TestCase):
    def fixture(self, version):
        temp = tempfile.TemporaryDirectory()
        self.addCleanup(temp.cleanup)
        root = Path(temp.name)
        proc = root / 'proc/self'
        proc.mkdir(parents=True)
        if version == 2:
            (proc / 'cgroup').write_text('0::/\n')
            (proc / 'mountinfo').write_text('1 2 0:1 /delegated/lab /sys/fs/cgroup ro - cgroup2 cgroup rw\n')
            values = {'memory.current': '1024', 'memory.max': '2048', 'cpu.stat': 'usage_usec 10000',
                      'cpu.max': '100000 100000', 'pids.current': '4', 'pids.max': '128'}
            folder = root / 'sys/fs/cgroup'
            folder.mkdir(parents=True)
            for name, value in values.items():
                (folder / name).write_text(value)
        else:
            controllers = {'memory': {'memory.usage_in_bytes': '1024', 'memory.limit_in_bytes': str(2**63 - 4096)},
                           'cpu': {'cpu.cfs_quota_us': '50000', 'cpu.cfs_period_us': '100000'},
                           'cpuacct': {'cpuacct.usage': '10000000'},
                           'pids': {'pids.current': '4', 'pids.max': 'max'}}
            (proc / 'cgroup').write_text(''.join(f'{i}:{name}:/services/lab\n' for i, name in enumerate(controllers, 1)))
            (proc / 'mountinfo').write_text(''.join(f'{i} 2 0:1 /services /sys/fs/cgroup/{name} ro - cgroup cgroup rw,{name}\n'
                                                   for i, name in enumerate(controllers, 1)))
            for name, values in controllers.items():
                folder = root / 'sys/fs/cgroup' / name / 'lab'
                folder.mkdir(parents=True)
                for key, value in values.items():
                    (folder / key).write_text(value)
        return Cgroups(root / 'proc', root)

    def test_v2_namespace_root_and_quota(self):
        c = self.fixture(2).counters()
        self.assertEqual((c['memory_limit_bytes'], c['cpu_ns'], c['cpu_limit_cores']), (2048, 10000000, 1))

    def test_v1_mount_root_and_unlimited_memory(self):
        c = self.fixture(1).counters()
        self.assertIsNone(c['memory_limit_bytes'])
        self.assertIsNone(c['pids_limit'])
        self.assertEqual(c['cpu_limit_cores'], 0.5)

    def test_cpu_is_normalized_to_container_quota(self):
        c = self.fixture(2).counters()
        second = dict(c, cpu_ns=c['cpu_ns'] + 800000000, cpu_limit_cores=1)
        result = resource_delta(c, second, 1)
        self.assertEqual(result['cpu_percent_of_limit'], 80)
        self.assertEqual(result['pressure'], ['cpu'])
        self.assertEqual(result['memory_percent_of_limit'], 50)

    def test_reset_counter_is_not_reported_healthy(self):
        c = self.fixture(2).counters()
        with self.assertRaises(RuntimeError):
            resource_delta(c, dict(c, cpu_ns=0), 1)


class MonitorTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.monitor = Monitor(Path(self.temp.name), Path(self.temp.name), cgroups=object())
        self.addCleanup(self.monitor.db.close)

    def test_history_retention_and_actual_coverage(self):
        now = time.time()
        self.monitor.record({'error': 'unavailable'}, now - 1810)
        self.monitor.record({'sample': 1}, now - 20)
        self.monitor.record({'sample': 2}, now)
        result = self.monitor.history(30)
        self.assertEqual(result['coverage']['samples'], 2)
        self.assertEqual(result['coverage']['covered_seconds'], 20)
        self.assertEqual(self.monitor.db.execute('SELECT COUNT(*) FROM samples').fetchone()[0], 2)

    def test_history_row_count_bound(self):
        now = time.time()
        for i in range(250):
            self.monitor.record({'sample': i}, now - 250 + i)
        self.assertEqual(self.monitor.db.execute('SELECT COUNT(*) FROM samples').fetchone()[0], 181)

    def test_empty_history_not_full_window(self):
        self.assertEqual(self.monitor.history(30)['coverage']['covered_seconds'], 0)
        self.assertIsNone(self.monitor.history(30)['coverage']['latest_age_seconds'])

    def test_input_bounds(self):
        for value in (0, 31, True, 2.5, '5'):
            with self.assertRaises(ValueError):
                self.monitor.history(value)
        for value in (0, 11, True, '1'):
            with self.assertRaises(ValueError):
                self.monitor.top_processes(value)
        with self.assertRaises(KeyError):
            self.monitor.query('SELECT * FROM users')
        self.assertEqual(set(QUERIES), {'os', 'processes', 'listeners'})
        self.assertTrue(all('LIMIT' in sql for sql in QUERIES.values()))

    def test_osquery_failure_propagates_instead_of_empty_evidence(self):
        import subprocess
        with patch('monitoring.subprocess.run', side_effect=subprocess.TimeoutExpired('osqueryi', 8)):
            with self.assertRaises(subprocess.TimeoutExpired):
                self.monitor.query('os')
        self.assertTrue(self.monitor.query_lock.acquire(blocking=False))
        self.monitor.query_lock.release()

    def test_reused_pid_has_unknown_cpu(self):
        old = dict(pid='7', start_time='100', parent='1', name='old', path='/old', resident_size='100', user_time='900', system_time='0')
        new = dict(old, start_time='200', name='new', user_time='0')
        with patch.object(self.monitor, 'query', side_effect=[[old], [new]]), patch('monitoring.time.sleep'), \
             patch.object(self.monitor, 'cgroups') as cg:
            cg.counters.return_value = {'cpu_limit_cores': 1}
            self.assertIsNone(self.monitor.top_processes()['by_cpu'][0]['cpu_percent_of_limit'])

    def test_service_failure_does_not_hide_other_applications(self):
        from io import BytesIO
        now = time.time()
        for name, pid in [('orders-api', 12), ('job-worker', 13)]:
            (self.monitor.state / (name + '.json')).write_text(json.dumps(dict(
                pid=pid, updated_at=now, completed=8, last_work_ms=2)))
        rows = [dict(pid='13', name='job-worker')]
        class Reply(BytesIO):
            status = 200
        def health(url, **_):
            if ':8081/' in url:
                raise OSError('unreachable')
            return Reply(b'{"requests": 4, "uptime_seconds": 20}')
        with patch.object(self.monitor, 'query', side_effect=[rows, []]), \
             patch('monitoring.urllib.request.urlopen', side_effect=health):
            apps = {row['name']: row for row in self.monitor.services()['applications']}
        self.assertEqual(apps['orders-api']['status'], 'down')
        self.assertIsNone(apps['orders-api']['pid'])
        self.assertEqual(apps['inventory-api']['status'], 'up')
        self.assertEqual(apps['job-worker']['status'], 'running')
        self.assertEqual(apps['report-cron']['status'], 'unknown')

    def test_stale_worker_heartbeat_is_not_reported_running(self):
        (self.monitor.state / 'job-worker.json').write_text(json.dumps(dict(
            pid=13, updated_at=time.time() - 40, completed=8, last_work_ms=2)))
        with patch.object(self.monitor, 'query', side_effect=[[dict(pid='13', name='job-worker')], []]), \
             patch('monitoring.urllib.request.urlopen', side_effect=OSError):
            apps = {row['name']: row for row in self.monitor.services()['applications']}
        self.assertEqual(apps['job-worker']['status'], 'unavailable')
        self.assertIsNone(apps['job-worker']['pid'])

    def test_scenario_commands_bounded_and_resettable(self):
        state = Path(self.temp.name)
        with patch.object(lab, 'STATE', state):
            for name in lab.SCENARIOS:
                lab.set_scenario(name, 20)
                record = json.loads((state / 'scenario.json').read_text())
                self.assertEqual(record['name'], name)
                self.assertLessEqual(record['expires_at'] - time.time(), 20)
            for seconds in (0, 9, 301):
                with self.assertRaises(ValueError):
                    lab.set_scenario('cpu', seconds)
            with self.assertRaises(ValueError):
                lab.set_scenario('shell')


if __name__ == '__main__':
    unittest.main()
