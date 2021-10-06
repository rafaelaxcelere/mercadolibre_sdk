from mercadolibre.src import error_handler, utils, shipping as ml_shipping


def get_order_from_resource(meli, resource):
    return meli.get_with_token(resource)


def get_billing_info(meli, order_id):
    return meli.get_with_token('/orders/{}/billing_info'.format(order_id))


class Buyer(object):

    def __init__(self, buyer_id, nickname, email):
        self.buyer_id = buyer_id
        self.nickname = nickname
        self.email = email
        self.billing_info = None

    @staticmethod
    def create_buyer_from_dic(dic, meli, order_id):
        buyer = Buyer(dic.get('id'), dic.get('nickname'), dic.get('email'))
        buyer.phone = ' '.join([dic.get('phone', {}).get('area_code') or '', dic.get('phone', {}).get('number') or ''])
        buyer.name = ' '.join([dic.get('first_name') or '', dic.get('last_name') or ''])
        buyer.billing_info = BillingInfo.create_billing_info_from_order_id(meli, order_id)
        return buyer


class BillingInfo(object):

    def __init__(self, doc_number, doc_type, name, fiscal_position):
        self.doc_number = doc_number
        self.doc_type = doc_type
        self.name = name
        self.fiscal_position = fiscal_position
        self.street = None
        self.zip = None
        self.city = None
        self.state = None

    @staticmethod
    def create_billing_info_from_order_id(meli, order_id):
        billing_info_meli = get_billing_info(meli, order_id)
        error_handler.RestErrorHandler.handle_error(billing_info_meli)
        billing_info_meli = billing_info_meli.json().get('billing_info', {})
        additional_info = billing_info_meli.get('additional_info', {})
        additional_info = BillingInfo.get_attribute_from_additional_info(additional_info)
        billing_info = BillingInfo(
            billing_info_meli.get('doc_number'),
            billing_info_meli.get('doc_type'),
            additional_info.get('name'),
            additional_info.get('fiscal_position')
        )
        billing_info.street = additional_info.get('street')
        billing_info.zip = additional_info.get('zip')
        billing_info.city = additional_info.get('city')
        billing_info.state = additional_info.get('state')
        return billing_info

    @staticmethod
    def get_attribute_from_additional_info(info):
        res = {'zip': None, 'city': None, 'street': None, 'state': None, 'fiscal_position': None, 'name': None}
        for dic in info:
            if dic.get('type') == 'ZIP_CODE':
                res['zip'] = dic.get('value')
                continue
            if dic.get('type') == 'STREET_NAME':
                res['street'] = dic.get('value')
                continue
            if dic.get('type') == 'TAXPAYER_TYPE_ID':
                res['fiscal_position'] = dic.get('value')
                continue
            if dic.get('type') == 'CITY_NAME':
                res['city'] = dic.get('value')
                continue
            if dic.get('type') == 'STATE_NAME':
                res['state'] = dic.get('value')
                continue
            if dic.get('type') == 'BUSINESS_NAME':
                res['name'] = dic.get('value')
                continue
        return res


class OrderItem(object):

    def __init__(self, item_id, quantity, unit_price, sku):
        self.item_id = item_id
        self.quantity = quantity
        self.unit_price = unit_price
        self.sku = sku

    @staticmethod
    def create_items_from_dic(dic):
        items = []
        for item in dic:
            dic_item = item.get('item')
            meli_item = OrderItem(
                dic_item.get('id'),
                item.get('quantity'),
                item.get('unit_price'),
                dic_item.get('seller_sku') or dic_item.get('seller_custom_field')
            )
            items.append(meli_item)
        return items


class Order(object):

    def __init__(self, order_id, currency_id, status, buyer, items, shipping):
        self.order_id = order_id
        self.buyer = buyer
        self.currency_id = currency_id
        self.status = status
        self.items = items
        self.shipping = shipping
        self.pack_id = None
        self.total_amount = None
        self.shipping_amount = None
        self.paid_amount = None
        self.date_closed = None

    @staticmethod
    def get_sale_info_from_resource(meli, resource):
        res = get_order_from_resource(meli, resource)
        error_handler.RestErrorHandler.handle_error(res)
        res = res.json()
        items = OrderItem.create_items_from_dic(res.get('order_items'))
        buyer = Buyer.create_buyer_from_dic(res.get('buyer'), meli, res.get('id'))
        shipping = ml_shipping.Shipping.create_shipping_from_id(meli, res.get('shipping', {}).get('id'))
        order = Order(res.get('id'), res.get('currency_id'), res.get('status'), buyer, items, shipping)
        order.pack_id = res.get('pack_id')
        order.total_amount = res.get('total_amount') or 0.0
        order.shipping_amount = shipping.cost or 0.0
        order.paid_amount = res.get('paid_amount') or 0.0
        if res.get('date_closed'):
            order.date_closed = utils.iso8601_to_datetime_utc(res.get('date_closed'))
        return order
