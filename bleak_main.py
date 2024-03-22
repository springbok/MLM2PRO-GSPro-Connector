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
        mlm2pro_client = None
        mlm2pro_api = None
        try:
            print(f'{scanner.device}')
            mlm2pro_client = MLM2PROClient(scanner.device)
            await mlm2pro_client.start()
            print(mlm2pro_client.is_connected)
            if mlm2pro_client.is_connected:
                mlm2pro_api = MLM2PROAPI(mlm2pro_client)
                await mlm2pro_api.start()
                result = await mlm2pro_api.auth()
                print(f'result: {result}')

                #print(f'firmware version: {await api.read_firmware_version()}')
        except Exception as e:
            print(f'Error: {format(e)}, {traceback.format_exc()}')
        finally:
            if mlm2pro_api is not None:
                await mlm2pro_api.stop()
            if mlm2pro_client is not None:
                await mlm2pro_client.stop()

    else:
        print('No device found')

if __name__ == '__main__':
    asyncio.run(main())
