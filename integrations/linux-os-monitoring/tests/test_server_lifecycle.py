"""Requires the integration's MCP dependencies; no osquery or container needed."""
import importlib.util
import importlib
import json
import sys
import threading
import time
import unittest
from pathlib import Path
from types import SimpleNamespace
from unittest.mock import patch

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))


@unittest.skipUnless(importlib.util.find_spec('mcp'), 'install integration requirements for ASGI lifecycle check')
class ServerLifecycleTests(unittest.TestCase):
    def test_workers_start_before_session_and_stop_on_shutdown(self):
        from starlette.testclient import TestClient

        started = [threading.Event(), threading.Event()]
        stopped = [threading.Event(), threading.Event()]
        calls = [0, 0]
        monitor = SimpleNamespace(last_sample=None, last_sample_ok=False)

        def worker(index, stop):
            calls[index] += 1
            if index == 0:
                monitor.last_sample = time.time()
                monitor.last_sample_ok = True
            started[index].set()
            stop.wait(10)
            stopped[index].set()

        monitor.collect = lambda stop: worker(0, stop)
        sys.modules.pop('server', None)
        with patch('monitoring.Monitor', return_value=monitor):
            server = importlib.import_module('server')
        self.addCleanup(sys.modules.pop, 'server', None)
        with patch.object(server, 'supervise', side_effect=lambda stop: worker(1, stop)), \
             patch.object(server, 'Path') as path:
            path.return_value.read_text.return_value = json.dumps({'updated_at': time.time()})
            with TestClient(server.create_app(), base_url='http://localhost:8000') as client:
                self.assertTrue(all(event.wait(2) for event in started))
                self.assertEqual(client.get('/healthz').status_code, 200)
                for request_id in (1, 2):
                    response = client.post('/mcp', headers={'Accept': 'application/json, text/event-stream'},
                                           json={'jsonrpc': '2.0', 'id': request_id, 'method': 'tools/list'})
                    self.assertEqual(response.status_code, 200)
                    self.assertEqual(len(response.json()['result']['tools']), 6)
                self.assertEqual(calls, [1, 1])
            self.assertTrue(all(event.is_set() for event in stopped))


if __name__ == '__main__':
    unittest.main()
