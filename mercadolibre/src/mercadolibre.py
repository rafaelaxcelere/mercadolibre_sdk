
from mercadolibre.python_sdk.lib import meli


class Mercadolibre(meli.Meli):

    def __init__(self, client_id, client_secret, access_token=None, refresh_token=None):
        super(Mercadolibre, self).__init__(
            client_id=client_id,
            client_secret=client_secret,
            access_token=access_token,
            refresh_token=refresh_token
        )

    def post_with_token(self, path, body=None, extra_headers=None):
        return self.post(path, body=body, params={'access_token': self.access_token}, extra_headers=extra_headers)

    def put_with_token(self, path, body=None, extra_headers=None):
        return self.put(path, body=body, params={'access_token': self.access_token}, extra_headers=extra_headers)

    def get_with_token(self, path, extra_headers=None):
        return self.get(path, params={'access_token': self.access_token}, extra_headers=extra_headers)
