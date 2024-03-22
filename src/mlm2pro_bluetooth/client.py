from bleak import BleakClient, BLEDevice


class Client:
    client: BleakClient
    #api: RadonEyeInterfaceBase

    def __init__(
        self,
        device: BLEDevice,
        connect_timeout: float = 10
    ) -> None:
        self.client = BleakClient(device, timeout=connect_timeout)
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
        await self.client.connect()  # type: ignore
        #self.__init_api()
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):  # type: ignore
        print('__aexit__')
        await self.client.disconnect()

    async def connect(self) -> None:
        print('connect')
        await self.client.connect()  # type: ignore
        #self.__init_api()

    async def disconnect(self) -> None:
        print('disconnect')
        await self.client.disconnect()  # type: ignore

    @property
    def is_connected(self) -> bool:
        return self.client.is_connected

    #async def beep(self) -> None:
    #    await self.api.beep(self.client)

    '''
    async def status(self) -> RadonEyeStatus:
        return await self.api.status(self.client)

    async def history(self) -> RadonEyeHistory:
        return await self.api.history(self.client)
    '''