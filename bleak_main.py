import asyncio

from src.mlm2pro_bluetooth.api import MLM2PROAPI
from src.mlm2pro_bluetooth.client import MLM2PROClient
from src.mlm2pro_bluetooth.scanner import MLM2PRODeviceScanner


async def main():
    device_scanner = MLM2PRODeviceScanner()
    loop = asyncio.get_event_loop()
    await device_scanner.run(loop)
    if device_scanner.device is not None:
        try:
            print(f'{device_scanner.device}')
            async with MLM2PROClient(device_scanner.device) as mlm2pro_client:
                print(mlm2pro_client.is_connected)
                api = MLM2PROAPI(mlm2pro_client)
                await api.init()
        except Exception as e:
            print(f'Error: {e}')
    else:
        print('No device found')

if __name__ == '__main__':
    asyncio.run(main())
