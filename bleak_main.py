import asyncio

from src.mlm2pro_bluetooth.client import Client
from src.mlm2pro_bluetooth.scanner import DeviceScanner


async def main():
    device_scanner = DeviceScanner()
    loop = asyncio.get_event_loop()
    await device_scanner.run(loop)
    if device_scanner.device is not None:
        print(f'{device_scanner.device}')
        async with Client(device_scanner.device) as client:
            print(client.is_connected)
            if not client.is_connected:
                await client.connect()
                await client.disconnect()
    else:
        print('No device found')

if __name__ == '__main__':
    asyncio.run(main())
