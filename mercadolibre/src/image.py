
def upload_image(meli, image):
    image_file = {'file': ('product.jpg', image, "image/jpeg")}
    return meli.upload("/pictures", image_file, {'access_token': meli.access_token})


class Image(object):

    def __init__(self, image, image_id):
        self.image = image
        self.image_id = image_id

    @staticmethod
    def upload(meli, image):
        return Image(meli, upload_image(meli, image).json().get('id'))
