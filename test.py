import asyncio
from bleak import BleakScanner, BleakClient

uuid_device_info = '0000180f-0000-1000-8000-00805f9b34fb'

async def main():
    devices = await BleakScanner.discover()
    dev = None
    for d in devices:
        print(d.name, d.address)
        #if "KICKR CORE " in d.name:
        if d.name and "MLM2-" in d.name or "BlueZ" in d.name: #or "KICKR CORE" in d.name:
            dev = d
            break
    if dev is not None:
        async with BleakClient(
                dev.address
        ) as client:
            print("connected")
            for service in client.services:
                print("[Service] %s", service)

                for char in service.characteristics:
                    if "read" in char.properties:
                        try:
                            value = await client.read_gatt_char(char.uuid)
                            print(
                                "  [Characteristic] %s (%s), Value: %r",
                                char,
                                ",".join(char.properties),
                                value,
                            )
                        except Exception as e:
                            print(
                                "  [Characteristic] %s (%s), Error: %s",
                                char,
                                ",".join(char.properties),
                                e,
                            )

                    else:
                        print(
                            "  [Characteristic] %s (%s)", char, ",".join(char.properties)
                        )

                    for descriptor in char.descriptors:
                        try:
                            value = await client.read_gatt_descriptor(descriptor.handle)
                            print("    [Descriptor] %s, Value: %r", descriptor, value)
                        except Exception as e:
                            print("    [Descriptor] %s, Error: %s", descriptor, e)

            print("disconnecting...")

        print("disconnected")
            
            #svcs = await client.get_services()
            #print("Services:")
            #for service in svcs:
            #    print(service)
            #device_info = await client.read_gatt_char(uuid_device_info)
            #print(device_info)


asyncio.run(main())