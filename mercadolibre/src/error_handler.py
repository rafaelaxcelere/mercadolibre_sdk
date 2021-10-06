# -*- encoding: utf-8 -*-


class InvalidTokenException(Exception):
    pass


class RestErrorHandler:

    @staticmethod
    def handle_error(response):
        response = response.json()
        if 'error' in response:
            message = response.get('message')
            if message in ['invalid_token', 'expired_token']:
                raise InvalidTokenException('El token que está tratando de utilizar es inválido')
            raise Exception("Error: {}\n{}".format(
                message, '\n'.join([cause.get('message') for cause in response.get('cause', []) or []])
            ))
