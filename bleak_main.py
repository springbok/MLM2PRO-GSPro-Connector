import asyncio
import traceback

import keyboard

from src.mlm2pro_bluetooth.manager import MLM2PROBluetoothManager


async def main():
    mlm2pro_manager = MLM2PROBluetoothManager()
    stop_event = asyncio.Event()
    try:
        await mlm2pro_manager.start()
        while not stop_event.is_set():
            try:
                await asyncio.sleep(1)
                print('waiting')
                if keyboard.is_pressed('q'):  # if key 'q' is pressed
                    print('stopping')
                    stop_event.set()
                    await mlm2pro_manager.stop()
            except Exception as e:
                stop_event.set()
                raise e
    except Exception as e:
        print(f'xxxxxxxxxxxxx Error: {format(e)}, {traceback.format_exc()}')
    finally:
        print('finally')
        await mlm2pro_manager.stop()
    mlm2pro_manager = None

if __name__ == '__main__':
    asyncio.run(main())
