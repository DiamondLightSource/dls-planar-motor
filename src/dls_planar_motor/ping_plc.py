import argparse
import asyncio

from asyncua import Client


class PingPLC(argparse.Action):
    def __init__(self, option_strings, dest, nargs=1, default="192.168.1.3", **kwargs):
        super().__init__(option_strings, dest, nargs=nargs, default=default, **kwargs)

    def __call__(self, parser, namespace, values, option_string=None):
        hostname = values[0]
        # Standard OPC UA endpoint URL pattern
        url = f"opc.tcp://{hostname}:4840"

        print(f"Connecting to OPC UA Server at {url}...")

        try:
            # Run the async connection check inside a synchronous block
            asyncio.run(self._test_connection(url))
            print(f"✅ Successfully connected to PLC OPC UA server at {hostname}!")
        except Exception as e:
            print(f"❌ Failed to connect to PLC at {hostname}.")
            print(f"Details: {e}")

        parser.exit()

    async def _test_connection(self, url: str):
        # Setting a short timeout so it fails quickly if the PLC drops
        async with Client(url=url, timeout=3) as client:
            health_node = client.get_node("ns=4;s=PLC_Healthy_Flag")
            test = await health_node.read_value()
            print(test)
