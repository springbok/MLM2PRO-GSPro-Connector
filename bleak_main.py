import asyncio

from src.mlm2pro_bluetooth.scanner import DeviceScanner

if __name__ == '__main__':
    my_scanner = DeviceScanner()
    loop = asyncio.get_event_loop()
    loop.run_until_complete(my_scanner.run(loop))