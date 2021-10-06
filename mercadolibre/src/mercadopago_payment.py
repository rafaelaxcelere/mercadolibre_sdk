from mercadolibre.src import error_handler


def post_payment(mpago, name, amount):
    return mpago.post_with_token("/checkout/preferences", body={'items': [{
        'title': name,
        'quantity': 1,
        'currency_id': 'ARS',
        'unit_price': amount,
    }]})

def get_payment_data(mpago, payment_id):
    res = mpago.get_with_token("/v1/payments/%s" % payment_id)
    error_handler.RestErrorHandler.handle_error(res)
    return res.json()
