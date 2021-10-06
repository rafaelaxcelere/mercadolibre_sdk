from . import mercadolibre
import requests


class Mercadopago(mercadolibre.Mercadolibre):

    def __init__(self, client_id, client_secret, access_token=None, refresh_token=None):
        super(Mercadopago, self).__init__(
            client_id=client_id,
            client_secret=client_secret,
            access_token=access_token,
            refresh_token=refresh_token
        )
        self.API_ROOT_URL = "https://api.mercadopago.com"
        self._requests = requests.Session()
        self._requests.verify = False
