from unidecode import unidecode

from mercadolibre.src import error_handler


class Attachment(object):

    def __init__(self, name, attachment):
        self.name = name
        self.attachment = attachment


class Message(object):

    def __init__(self, seller_id, buyer_id, resource, resource_id, text):
        self.seller_id = seller_id
        self.buyer_id = buyer_id
        self.resource = resource
        self.resource_id = resource_id
        self.text = text
        self.attachments = None

    def send_messages(self, meli):
        """
        Intenta enviar un mensaje interno en mercadolibre para un recurso.
        Si la mensajería está bloqueada devuelve False
        """
        # Verificamos si acepta mensajería antes de enviar el mensaje
        res = meli.get_with_token('/messages/{}/{}'.format(self.resource, self.resource_id))
        error_handler.RestErrorHandler.handle_error(res)
        if res.json().get('conversation', {}).get('status') == 'blocked':
            return False
        item = {
            'from': {'user_id': self.seller_id},
            'to': [{"user_id": self.buyer_id, "resource": self.resource,
                    "resource_id": self.resource_id}],
            'text': self.text
        }
        if self.attachments:
            attachments = []
            for attachment in self.attachments:
                attachment_file = {'file': (unidecode(attachment.name), attachment.attachment, "application/pdf")}
                response = meli.upload(
                    '/messages/attachments',
                    attachment_file,
                    {'access_token': meli.access_token}
                )
                if not response.ok or not response.json().get('id'):
                    raise Exception("Hubo un error al intentar subir el adjunto en mercadolibre: {}".format(
                        response.json().get('message')
                    ))

                attachments.append(response.json().get('id'))

            item['attachments'] = attachments

        res = meli.post_with_token('/messages/{}/{}'.format(self.resource, self.resource_id), item)
        error_handler.RestErrorHandler.handle_error(res)
        return True
