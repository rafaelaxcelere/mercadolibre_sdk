def get_listing_types(meli_site):
    return meli_site.get_with_token('/listing_types')


class ListingType(object):

    def __init__(self, name, listing_type_id):
        self.name = name
        self.listing_type_id = listing_type_id

    @staticmethod
    def get_listing_type_instances(meli_site):
        return [ListingType(listing_type.get('name'), listing_type.get('id'))
                for listing_type in get_listing_types(meli_site).json()]
