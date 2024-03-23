import asyncio
import traceback

from src.appdata import AppDataPaths
from src.mlm2pro_bluetooth.manager import MLM2PROBluetoothManager


async def main():
    mlm2pro_manager = MLM2PROBluetoothManager()
    error = False
    try:
        await mlm2pro_manager.start()
        while not error:
            await asyncio.sleep(1)
    except Exception as e:
        print(f'Error: {format(e)}, {traceback.format_exc()}')
        error = True
    finally:
        await mlm2pro_manager.stop()

if __name__ == '__main__':
    asyncio.run(main())
