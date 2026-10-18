"""Exercise the real MCP protocol and assert the six read-only tool contracts."""
import argparse
import asyncio
import json

from mcp import ClientSession
from mcp.client.streamable_http import streamablehttp_client

EXPECTED = {'get_system_overview', 'get_resource_usage', 'get_top_processes',
            'get_filesystem_usage', 'get_service_network_status', 'get_recent_history'}


async def check(url):
    async with streamablehttp_client(url) as (read, write, _):
        async with ClientSession(read, write) as session:
            await session.initialize()
            found = {tool.name for tool in (await session.list_tools()).tools}
            assert found == EXPECTED, found
            result = {}
            for name in sorted(found):
                reply = await session.call_tool(name, {})
                assert not reply.isError, reply
                data = reply.structuredContent or json.loads(reply.content[0].text)
                assert data.get('scope') and data.get('observed_at'), data
                result[name] = data
            # Neither arbitrary SQL nor scenario control is an exported MCP tool.
            bad = await session.call_tool('get_recent_history', {'minutes': 31})
            assert bad.isError, 'Out-of-range history request unexpectedly accepted'
            print(json.dumps(result, indent=2))


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--url', required=True)
    asyncio.run(check(parser.parse_args().url))
