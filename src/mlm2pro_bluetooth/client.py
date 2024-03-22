from bleak import BleakClient, BLEDevice
from bleak.backends.service import BleakGATTService


class MLM2PROClient:


    def __init__(
        self,
        device: BLEDevice,
        connect_timeout: float = 10
    ) -> None:
        self.bleak_client = BleakClient(device, timeout=connect_timeout)
        self.connect_timeout = connect_timeout

    '''
    def __init_api(self) -> None:
        self.api = RadonEyeInterfaceFactory.create(
            self.client,
            status_read_timeout=self.status_read_timeout,
            history_read_timeout=self.history_read_timeout,
        )
    '''

    async def __aenter__(self):
        print('__aenter__')
        await self.connect()  # type: ignore
        #self.__init_api()
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):  # type: ignore
        print('__aexit__')
        await self.disconnect()

    async def connect(self) -> None:
        print('connect')
        if not self.is_connected:
            await self.bleak_client.connect()  # type: ignore
            #await self.bleak_client.pair()
            #self.__init_api()

    async def disconnect(self) -> None:
        print('disconnect')
        if self.is_connected:
            #await self.bleak_client.unpair()
            await self.bleak_client.disconnect()  # type: ignore

    @property
    def is_connected(self) -> bool:
        return self.bleak_client.is_connected

    async def supports_service(self, uuid) -> bool:
        return bool(await self.get_service(uuid))

    async def get_service(self, uuid) -> BleakGATTService:
        return self.bleak_client.services.get_service(uuid)

    '''
    async def status(self) -> RadonEyeStatus:
        return await self.api.status(self.client)

    async def history(self) -> RadonEyeHistory:
        return await self.api.history(self.client)
    '''