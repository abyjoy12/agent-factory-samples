"""Six read-only tools over stateless Streamable HTTP /mcp."""
import asyncio
import os
import json
import time
import threading
from contextlib import asynccontextmanager
from pathlib import Path

from mcp.server.fastmcp import FastMCP
from mcp.server.transport_security import TransportSecuritySettings
from starlette.responses import JSONResponse

from lab import supervise
from monitoring import Monitor

monitor = Monitor()


@asynccontextmanager
async def lifespan(_app):
    stop = threading.Event()
    threads = [threading.Thread(target=target, args=(stop,), daemon=True)
               for target in (monitor.collect, supervise)]
    for thread in threads:
        thread.start()
    try:
        async with mcp.session_manager.run():
            yield
    finally:
        stop.set()
        for thread in threads:
            await asyncio.to_thread(thread.join, 5)


mcp = FastMCP('Linux OS Monitoring', host='0.0.0.0', port=8000,
              instructions='Read-only evidence about Linux machine linux-ops-01 and its applications. '
                           'Use the measured assigned resource limits and actual observation coverage.',
              json_response=True, stateless_http=True,
              transport_security=TransportSecuritySettings(
                  allowed_hosts=os.getenv('MCP_ALLOWED_HOSTS', '127.0.0.1:*,localhost:*').split(','),
                  allowed_origins=os.getenv('MCP_ALLOWED_ORIGINS', 'http://localhost:*').split(',')))


@mcp.tool()
async def get_system_overview() -> dict:
    """Read Linux OS identity, assigned CPU/memory limits, operations filesystem and history coverage."""
    return await asyncio.to_thread(monitor.overview)


@mcp.tool()
async def get_resource_usage() -> dict:
    """Measure Linux machine CPU over one second, charged memory, assigned limits and process count."""
    return await asyncio.to_thread(monitor.resources)


@mcp.tool()
async def get_top_processes(limit: int = 5) -> dict:
    """Read bounded osquery process samples, top CPU and RSS consumers. limit: 1–10."""
    return await asyncio.to_thread(monitor.top_processes, limit)


@mcp.tool()
async def get_filesystem_usage() -> dict:
    """Measure bytes and inodes on the configured /var/lib/operations filesystem."""
    return await asyncio.to_thread(monitor.filesystem)


@mcp.tool()
async def get_service_network_status() -> dict:
    """Check orders-api:8081, inventory-api:8082, job-worker, report-cron and log-forwarder; read osquery listeners."""
    return await asyncio.to_thread(monitor.services)


@mcp.tool()
async def get_recent_history(minutes: int = 5) -> dict:
    """Read actual 10-second samples retained for at most 30 minutes. minutes: 1–30. Report gaps."""
    return await asyncio.to_thread(monitor.history, minutes)


@mcp.custom_route('/healthz', methods=['GET'])
async def health(_request):
    age = time.time() - monitor.last_sample if monitor.last_sample is not None else None
    try:
        supervisor_fresh = time.time() - json.loads(Path('/run/lab/status.json').read_text())['updated_at'] < 10
    except (OSError, ValueError, KeyError):
        supervisor_fresh = False
    ready = age is not None and age < 30 and monitor.last_sample_ok and supervisor_fresh
    return JSONResponse({'ready': ready, 'latest_sample_age_seconds': age}, status_code=200 if ready else 503)


def create_app():
    # FastMCP's server lifespan runs per request in stateless HTTP mode. Start
    # collection/simulation with the ASGI application so readiness works before
    # the first client connects and subsequent requests cannot duplicate workers.
    app = mcp.streamable_http_app()
    app.router.lifespan_context = lifespan
    return app


if __name__ == '__main__':
    import uvicorn
    uvicorn.run(create_app(), host='0.0.0.0', port=8000)
