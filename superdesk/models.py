from __future__ import unicode_literals

from collections import deque
from mongoengine import *

class Ref(EmbeddedDocument):
    idRef = StringField()
    itemClass = StringField()
    residRef = StringField()
    href = StringField()
    size = IntField()
    rendition = StringField()
    contentType = StringField()
    format = StringField()

class Group(EmbeddedDocument):
    """Group
    """
    id = StringField()
    role = StringField()
    mode = StringField()
    refs = ListField(EmbeddedDocumentField(Ref))

class Content(EmbeddedDocument):
    """Content
    """
    contenttype = StringField()
    content = StringField()
    residRef = StringField()
    href = StringField()
    size = IntField()
    rendition = StringField()
    storage = StringField()

class Item(Document):
    """anyItem"""

    CLASS_TEXT = 'icls:text'
    CLASS_PACKAGE = 'icls:composite'

    guid = StringField(unique=True)
    version = IntField(required=True)
    itemClass = StringField()
    urgency = StringField()
    headline = StringField()
    slugline = StringField()
    byline = StringField()
    creditline = StringField()
    firstCreated = DateTimeField()
    versionCreated = DateTimeField()

    groups = ListField(EmbeddedDocumentField(Group))
    contents = ListField(EmbeddedDocumentField(Content))

    copyrightHolder = StringField()

    meta = {
        'collection': 'items',
        'allow_inheritance': False,
        'indexes': [('itemClass', '-versionCreated')]
        }

    def get_refs(self, role):
        items = []
        queue = deque((role,))
        while len(queue):
            role = queue.popleft()
            refs = []
            for group in self.groups:
                if group.id == role:
                    refs += group.refs
            for ref in refs:
                if ref.idRef:
                    queue.append(ref.idRef)
                else:
                    items.append(ref)
        return items

    def is_package(self):
        return self.itemClass == self.CLASS_PACKAGE

def get_last_update():
    item = Item.objects.only('versionCreated').order_by('-versionCreated').first()
    if item:
        return item.versionCreated
