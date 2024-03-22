from src.mlm2pro_bluetooth.client import MLM2PROClient


class MLM2PROAPI:


    service_uuid = '0000180a-0000-1000-8000-00805f9b34fb'
    #service_uuid = 'DAF9B2A4-E4DB-4BE4-816D-298A050F25CD'
    firmware_characteristic_uuid = '00002a29-0000-1000-8000-00805f9b34fb'

    def __init__(self, client: MLM2PROClient):
        self.mlm2pro_client = client
        self.general_service = None

    async def init(self):
        self.general_service = await self.mlm2pro_client.get_service(MLM2PROAPI.service_uuid)
        if self.general_service is None:
            raise Exception('General service not found')
        print('init completed')
        return self.general_service