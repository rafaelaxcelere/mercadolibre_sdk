from mercadolibre.src import error_handler


def get_merchant_order_data(mpago, order_id):
    res = mpago.get_with_token("/merchant_orders/%s" % order_id)
    error_handler.RestErrorHandler.handle_error(res)
    return res.json()
