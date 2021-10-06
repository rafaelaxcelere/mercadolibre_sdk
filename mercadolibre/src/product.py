from . import error_handler


def get_publication_from_id(meli, product_id):
    return meli.get_with_token('/items/{}?include_attributes=all'.format(product_id))


def get_publication_description_from_id(meli, product_id):
    return meli.get_with_token('/items/{}/description'.format(product_id))


class Product(object):

    def __init__(self, title=None, category_id=None, price=None, currency_id=None,
                 available_quantity=None, listing_type_id=None):
        self.title = title
        self.category_id = category_id
        self.price = price
        self.currency_id = currency_id
        self.available_quantity = available_quantity
        self.listing_type_id = listing_type_id
        self.buying_mode = None
        self.condition = None
        self.video_id = None
        self.pictures = []
        self.shipping_mode = None
        self.product_id = None
        self.permalink = None
        self.description = None
        self.variations = []
        self.sku = None
        self.status = None

    @staticmethod
    def get_product_from_id(meli, product_id):
        res = get_publication_from_id(meli, product_id)
        error_handler.RestErrorHandler.handle_error(res)
        description = get_publication_description_from_id(meli, product_id)
        error_handler.RestErrorHandler.handle_error(description)
        res = res.json()
        product = Product(res.get('title'), res.get('category_id'), res.get('price'), res.get('currency_id'),
                          res.get('available_quantity'), res.get('listing_type_id'))
        product.description = description.json().get('plain_text')
        product.buying_mode = res.get('buying_mode')
        product.condition = res.get('condition')
        product.video_id = res.get('video_id')
        product.pictures = res.get('pictures')
        product.shipping_mode = res.get('shipping', {}).get('mode')
        product.product_id = res.get('id')
        product.permalink = res.get('permalink')
        product.status = res.get('status')
        product.sku = res.get('seller_custom_field')
        if not product.sku:
            for attribute in res.get('attributes', []):
                if attribute.get('id') == 'SELLER_SKU':
                    product.sku = attribute.get('value_name')
                    break

        if res.get('variations'):
            variations = []
            for variation in res.get('variations'):
                new_variation = Variant()
                new_variation.product_id = variation.get('id')
                new_variation.sku = variation.get('seller_custom_field')
                if not new_variation.sku:
                    for attribute in variation.get('attributes'):
                        if attribute.get('id') == 'SELLER_SKU':
                            new_variation.sku = attribute.get('value_name')
                            break
                variations.append(new_variation)
            product.variations = variations
        return product

    def get_body(self):
        body = {
            'title': self.title,
            'category_id': self.category_id,
            'price': self.price,
            'listing_type_id': self.listing_type_id,
            'buying_mode': self.buying_mode,
            'condition': self.condition,
            'video_id': self.video_id,
            'pictures': self.pictures,
            'available_quantity': self.available_quantity,
            'description': {
                'plain_text': self.description,
            }
        }
        if self.shipping_mode:
            body['shipping'] = {
                'mode': self.shipping_mode
            }

        if self.sku:
            body['seller_custom_field'] = self.sku

        return body

    def publish(self, meli):
        body = self.get_body()
        description = body.get('description', {}).get('plain_text', '')
        body.update({
            'currency_id': self.currency_id
        })
        if self.variations:
            body['variations'] = [
                {
                    'attribute_combinations': [
                        {
                            "name": attribute.attribute_id,
                            "value_name": attribute.value,
                        }
                        for attribute in variant.attribute_combinations
                    ],
                    'available_quantity': variant.available_quantity,
                    'price': variant.price,
                    'attributes': [
                        {
                            "id": "SELLER_SKU",
                            "value_name": variant.sku,
                        }
                    ] + variant.attributes,
                    'picture_ids': variant.pictures
                }
                for variant in self.variations
            ]

        response = meli.post_with_token('/items', body)
        error_handler.RestErrorHandler.handle_error(response)
        res = response.json()
        self.product_id = res.get('id')

        self.update_description(meli, description)

        # Tenemos que mapear el id de la variante matcheando por SKU
        if self.variations:
            for variation in self.variations:
                for meli_variation in res.get('variations'):
                    for meli_attribute in meli_variation.get('attributes'):
                        if meli_attribute.get('id') == 'SELLER_SKU' \
                                and meli_attribute.get('value_name') == variation.sku:
                            variation.product_id = meli_variation.get('id')

        self.permalink = res.get('permalink')

    def update_description(self, meli, description):
        if description:
            response = meli.put_with_token(
                '/items/{}/description'.format(self.product_id),
                {'plain_text': description}
            )
            error_handler.RestErrorHandler.handle_error(response)

    def update(self, meli):
        body = self.get_body()
        # La descripción se actualiza con un put aislado
        description = body.get('description', {}).get('plain_text', '')
        body.pop('description')
        # El manejo de fotos es a parte
        body.pop('pictures')
        # Estos campos no se pueden sincronizar en publicaciones con ventas.
        body.pop('category_id')
        body.pop('buying_mode')
        body.pop('condition')
        body.pop('listing_type_id')
        if self.variations:
            # Si estoy actualizando una publicación con variantes, no debo enviar el price (se informa en las variantes)
            if len(self.variations) > 1:
                body.pop('price')
            body.pop('available_quantity')
            variations = []
            for variant in self.variations:
                if variant.product_id:
                    variant_attrs = {
                        'price': variant.price,
                        'available_quantity': variant.available_quantity,
                        'id': variant.product_id,
                    }
                elif variant.attribute_combinations:
                    # Caso de variacion nueva que no existia
                    variant_attrs = {
                        'attribute_combinations': [
                            {
                                "name": attribute.attribute_id,
                                "value_name": attribute.value,
                            }
                            for attribute in variant.attribute_combinations
                        ],
                        'available_quantity': variant.available_quantity,
                        'price': variant.price,
                        'attributes': [
                                          {
                                              "id": "SELLER_SKU",
                                              "value_name": variant.sku,
                                          }
                                      ] + variant.attributes,
                        'picture_ids': variant.pictures
                    }
                else:
                    continue
                variations.append(variant_attrs)

            body['variations'] = variations

        try:
            self.update_description(meli, description)
            response = meli.put_with_token('/items/{}'.format(self.product_id), body)
            error_handler.RestErrorHandler.handle_error(response)
        except Exception as e:
            raise Exception(e.args[0])

        for variation in self.variations:
            for meli_variation in response.json().get('variations'):
                for meli_attribute in meli_variation.get('attributes'):
                    if meli_attribute.get('id') == 'SELLER_SKU' \
                            and meli_attribute.get('value_name') == variation.sku:
                        variation.product_id = meli_variation.get('id')

    def update_pictures(self, meli):
        body = {'pictures': self.pictures}
        if self.variations:
            variations = []
            for variation in self.variations:
                variations.append({'id': variation.product_id, 'picture_ids': variation.pictures})
                for picture in variation.pictures:
                    body['pictures'].append({'id': picture})
            body['variations'] = variations

        response = meli.put_with_token('/items/{}'.format(self.product_id), body)
        error_handler.RestErrorHandler.handle_error(response)

    def update_status(self, meli, state):
        body = {
            'status': state
        }
        response = meli.put_with_token('/items/{}'.format(self.product_id), body)
        error_handler.RestErrorHandler.handle_error(response)

    def update_stock(self, meli):
        if not self.product_id:
            raise Exception("El producto a actualizar no tiene ID")

        if self.variations:
            variations = []
            for variation in self.variations:
                if not variation.product_id:
                    raise Exception("El producto a actualizar no tiene ID")
                vals = {'id': variation.product_id}
                vals['available_quantity'] = variation.available_quantity or 0.0

                variations.append(vals)

            body = {
                'variations': variations,
            }
            response = meli.put_with_token('/items/{}'.format(self.product_id), body)
            error_handler.RestErrorHandler.handle_error(response)
        else:
            body = {
                'available_quantity': self.available_quantity
            }
            response = meli.put_with_token('/items/{}'.format(self.product_id), body)
            error_handler.RestErrorHandler.handle_error(response)


class Variant(object):

    def __init__(self, attribute_combinations=None, available_quantity=None, price=None, pictures=None, sku=None):
        self.attribute_combinations = attribute_combinations
        self.available_quantity = available_quantity
        self.price = price
        self.pictures = pictures
        self.sku = sku
        self.product_id = None
        self.attributes = []


class AttributeCombination(object):

    def __init__(self, attribute_id, value):
        self.attribute_id = attribute_id
        self.value = value
