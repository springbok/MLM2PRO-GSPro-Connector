import asyncio
import traceback

from src.mlm2pro_bluetooth.api import MLM2PROAPI
from src.mlm2pro_bluetooth.client import MLM2PROClient
from src.mlm2pro_bluetooth.scanner import MLM2PROScanner

device = None

async def main():
    scanner = MLM2PROScanner()
    loop = asyncio.get_event_loop()
    await scanner.run(loop)

    if scanner.device is not None:
        print(f"Device: {scanner.device}")
        try:
            print(f'{scanner.device}')
            async with MLM2PROClient(scanner.device) as mlm2pro_client:
                print(mlm2pro_client.is_connected)
                async with MLM2PROAPI(mlm2pro_client) as api:
                    result = await api.auth()
                    print(f'result: {result}')

                #print(f'firmware version: {await api.read_firmware_version()}')
        except Exception as e:
            print(f'Error: {format(e)}, {traceback.format_exc()}')

    else:
        print('No device found')

if __name__ == '__main__':
    asyncio.run(main())
