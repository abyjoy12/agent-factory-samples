"""Operator acceptance check: inject bounded lab faults, assert MCP evidence, reset.

Run inside the deployed lab container via `podman exec -i ... python -`.
This is an operator script, never an MCP tool. Takes about 90 seconds.
"""
import asyncio
import json
import time
from pathlib import Path

import httpx
from mcp import ClientSession
from mcp.client.streamable_http import streamablehttp_client

from lab import set_scenario

EXPECTED = {'get_system_overview', 'get_resource_usage', 'get_top_processes',
            'get_filesystem_usage', 'get_service_network_status', 'get_recent_history'}


async def check():
    if not Path('/app/lab.py').is_file() or not Path('/var/lib/operations').is_mount():
        raise RuntimeError('Run this operator check inside the Linux monitoring lab container')
    evidence = {}
    async with streamablehttp_client('http://127.0.0.1:8000/mcp') as (read, write, _):
        async with ClientSession(read, write) as session:
            await session.initialize()
            assert {tool.name for tool in (await session.list_tools()).tools} == EXPECTED

            async def call(name, **args):
                reply = await session.call_tool(name, args)
                assert not reply.isError, reply
                data = reply.structuredContent or json.loads(reply.content[0].text)
                assert data['scope'] and data['observed_at'], data
                return data

            def record(name, data):
                evidence[name] = data
                print(json.dumps({name: data}), flush=True)

            try:
                set_scenario('normal')
                await asyncio.sleep(2)
                baseline = await call('get_system_overview')
                assert baseline['resources']['cpu_limit_cores'] == 1
                assert baseline['resources']['memory_limit_bytes'] == 1536 * 1024**2
                assert baseline['resources']['pids_limit'] == 128
                assert not baseline['filesystem']['pressure']
                applications = (await call('get_service_network_status'))['applications']
                assert len(applications) == 5, applications
                assert all(row['status'] in ('up', 'running') for row in applications), applications
                initial = {row['name']: row for row in applications}
                await asyncio.sleep(12)
                applications = (await call('get_service_network_status'))['applications']
                assert all(row['pid'] == initial[row['name']]['pid'] for row in applications)
                assert all(row.get('requests', row['completed']) > initial[row['name']].get('requests', initial[row['name']]['completed'])
                           for row in applications), applications
                quiet = await call('get_resource_usage')
                assert quiet['cpu_percent_of_limit'] < 15 and quiet['memory_percent_of_limit'] < 25, quiet
                record('applications', applications)
                record('baseline', baseline)

                set_scenario('cpu', 90)
                await asyncio.sleep(2)
                cpu = await call('get_resource_usage')
                top = await call('get_top_processes')
                assert cpu['cpu_percent_of_limit'] >= 75, cpu
                assert any(row['name'] == 'batch-indexer' and (row['cpu_percent_of_limit'] or 0) > 50
                           for row in top['by_cpu']), top
                await asyncio.sleep(25)
                history = await call('get_recent_history', minutes=1)
                assert history['coverage']['covered_seconds'] >= 20, history
                assert sum('cpu' in row.get('resources', {}).get('pressure', [])
                           for row in history['samples']) >= 2, history
                record('cpu', dict(resources=cpu, processes=top, coverage=history['coverage']))

                set_scenario('memory', 90)
                await asyncio.sleep(2)
                early = await call('get_resource_usage')
                await asyncio.sleep(16)
                late = await call('get_resource_usage')
                top = await call('get_top_processes')
                assert late['memory_bytes'] > early['memory_bytes'] + 300 * 1024**2, (early, late)
                assert 'memory' in late['pressure'], late
                assert any(row['name'] == 'cache-builder' and row['resident_size_bytes'] > 1024**3
                           for row in top['by_memory']), top
                record('memory', dict(early=early, late=late, processes=top))

                set_scenario('disk', 30)
                await asyncio.sleep(2)
                disk = await call('get_filesystem_usage')
                assert disk['pressure'] and disk['capacity_bytes'] == 64 * 1024**2, disk
                record('disk', disk)

                set_scenario('service-down', 10)
                await asyncio.sleep(2)
                service = await call('get_service_network_status')
                apps = {row['name']: row for row in service['applications']}
                assert not apps['orders-api']['reachable'] and apps['inventory-api']['reachable'], service
                assert all(row['pid'] == initial[row['name']]['pid'] for row in service['applications']
                           if row['name'] != 'orders-api'), service
                assert not any(int(row['port']) == 8081 for row in service['listeners']), service
                assert any(int(row['port']) == 8000 for row in service['listeners']), service
                async with httpx.AsyncClient() as client:
                    assert (await client.get('http://127.0.0.1:8000/healthz')).status_code == 200
                record('service_down', service)
                await asyncio.sleep(10)
                recovered = await call('get_service_network_status')
                assert all(row['status'] in ('up', 'running') for row in recovered['applications']), recovered
                assert not (await call('get_filesystem_usage'))['pressure']
                assert (await call('get_resource_usage'))['memory_percent_of_limit'] < 75
                bad = await session.call_tool('get_recent_history', {'minutes': 31})
                assert bad.isError
                record('recovered_after_expiry', recovered)
            finally:
                set_scenario('normal')
                await asyncio.sleep(2)
    print('PASS: six tools, baseline, four faults, bounded history, invalid input, TTL and reset', flush=True)


if __name__ == '__main__':
    asyncio.run(check())
