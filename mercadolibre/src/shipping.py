

def get_shippings_tags(meli, shipping_ids):
    response = meli.get('/shipment_labels', {'access_token': meli.access_token, 'shipment_ids': shipping_ids})
    if not response.ok:
        raise Exception("Hubo un error al intentar descargar la(s) etiqueta(s)")
    return response.content


def get_shipping(meli, shipping_id):
    return meli.get_with_token('/shipments/{}'.format(shipping_id))


def get_shipment_items_from_resource(meli, resource):
    return meli.get_with_token('{}/items'.format(resource))


class Shipping(object):

    def __init__(self, shipping_id=None):
        self.shipping_id = shipping_id
        self.status = None
        self.address_line = None
        self.zip_code = None
        self.city = None
        self.state = None
        self.cost = None
        self.logistic_type = None
        self.shipping_method_name = None
        self.tracking_number = None
        self.tracking_method = None

    @staticmethod
    def get_order_ids_from_shipment_resource(meli, shipping_id):
        try:
            items = get_shipment_items_from_resource(meli, shipping_id).json()
        except Exception:
            return []

        return [item.get('order_id') for item in items]

    @staticmethod
    def create_shipping_from_id(meli, shipping_id):
        shipping = Shipping(shipping_id)
        try:
            dic = get_shipping(meli, shipping_id).json()
        except Exception:
            return shipping

        address = dic.get('receiver_address', {})
        shipping.status = dic.get('status')
        shipping.address_line = address.get('address_line')
        shipping.zip_code = address.get('zip_code')
        shipping.city = address.get('city', {}).get('name')
        shipping.state = address.get('state', {}).get('name')
        shipping.logistic_type = dic.get('logistic_type')
        shipping.tracking_number = dic.get('tracking_number')
        shipping.tracking_method = dic.get('tracking_method')
        shipping.cost = dic.get('shipping_option', {}).get('cost')
        shipping.shipping_method_name = dic.get('shipping_option', {}).get('name')
        return shipping
