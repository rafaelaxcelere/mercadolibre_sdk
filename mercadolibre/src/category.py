# -*- encoding: utf-8 -*-

def get_main_categories(meli_site):
    return meli_site.get_with_token('/categories')


def get_category(meli, category_id):
    return meli.get_with_token('/categories/{}'.format(category_id))


class Category(object):

    def __init__(self, name, category_id, listing_allowed):
        self.name = name
        self.category_id = category_id
        self.listing_allowed = listing_allowed

    @staticmethod
    def get_main_categories_instances(meli_site):
        # Las categorías principales no son publicables
        return [Category(category.get('name'), category.get('id'), False)
                for category in get_main_categories(meli_site).json()]

    @staticmethod
    def get_children_categories(meli, category_id):
        categories = []
        for category in get_category(meli, category_id).json().get('children_categories', []):
            sub_category = get_category(meli, category.get('id')).json()
            categories.append(Category(
                sub_category.get('name'),
                sub_category.get('id'),
                sub_category.get('settings', {}).get('listing_allowed'))
            )
        return categories

    @staticmethod
    def get_categories_to_root(meli, category_id):
        categories = []
        for category in get_category(meli, category_id).json().get('path_from_root', []):
            res_category = get_category(meli, category.get('id')).json()
            categories.append(Category(
                res_category.get('name'),
                res_category.get('id'),
                res_category.get('settings', {}).get('listing_allowed'))
            )
        return categories
