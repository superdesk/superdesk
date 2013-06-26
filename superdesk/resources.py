from types import Resource
from models import Item

class Items(Resource):
    '''Items resource.'''

    def get(self):
        return list(Item.objects[:50])
