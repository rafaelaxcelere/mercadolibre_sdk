from . import mercadolibre


class MercadolibreSite(mercadolibre.Mercadolibre):

    def __init__(self, client_id, client_secret, access_token=None, refresh_token=None, site='MLA'):
        super(MercadolibreSite, self).__init__(
            client_id=client_id,
            client_secret=client_secret,
            access_token=access_token,
            refresh_token=refresh_token
        )
        self.site = site

    def get_with_token(self, path, extra_headers=None):
        path = '/sites/{}{}'.format(self.site, path)
        return self.get(path, params={'access_token': self.access_token}, extra_headers=extra_headers)
