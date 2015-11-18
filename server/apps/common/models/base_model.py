# -*- coding: utf-8; -*-
#
# This file is part of Superdesk.
#
# Copyright 2013, 2014 Sourcefabric z.u. and contributors.
#
# For the full copyright and license information, please see the
# AUTHORS and LICENSE files distributed with this source code, or
# at https://www.sourcefabric.org/superdesk/license


class InvalidFilter(Exception):
    def __init__(self, filter, operation):
        self.filter = filter
        self.operation = operation

    def __str__(self):
        return 'Invalid filter on %s: %s' % (self.operation, filter)


class InvalidEtag(Exception):
    def __str__(self):
        return 'Client and server etags don\'t match'


class Validator():
    def validate(self, doc):
        raise NotImplementedError()


class ValidationError():
    def __init__(self, errors):
        self.errors = errors


class BaseModel():
    """
    This is a basic interface for defining models. The only requirement is
    to implement the name method that uniquely identifies a model.
    """

    def __init__(self, resource, data_layer, schema, validator):
        """
        @param resource: str
            The resource name
        @param data_layer: object
            The object that implements the database operations.
        @param schema: dict
            The model schema definition
        @param validator: object
            The object that validates the model data.
        """
        self.resource = resource
        self.data_layer = data_layer
        self.schema = schema
        self.validator = validator

    @classmethod
    def name(cls):
        raise NotImplementedError()

    def on_create(self, docs):
        """
        Method called before the create operation.
        @param docs: list of docs to be inserted
        """

    def on_created(self, docs):
        """
        Method called after the create operation.
        @param docs: list of inserted docs
        """

    def on_update(self, doc, orig):
        """
        Method called before the update/replace operations.
        @param doc: the document updates
        @param orig: the original document before the update
        """

    def on_updated(self, doc, orig):
        """
        Method called after the update/replace operations.
        @param doc: the document updates
        @param orig: the original document before the update
        """

    def on_delete(self, docs):
        """
        Method called before the delete operation.
        @param docs: list of docs to be deleted
        """

    def on_deleted(self, docs):
        """
        Method called after the delete operation.
        @param docs: list of deleted docs
        """

    def etag(self, doc):
        """
        Return the document etag.
        """
        return self.data_layer.etag(doc)

    def validate_etag(self, doc, etag):
        """
        Validates the given etag for the given document.
        Raises InvalidEtag if they don't match.
        """
        if self.etag(doc) != etag:
            raise InvalidEtag()

    def find_one(self, filter, projection=None):
        """
        Return one document selected based on the given filter.
        @param filter: dict
        @param projection: dict
        """
        return self.data_layer.find_one(self.resource, filter, projection)

    def find(self, filter, projection=None, **options):
        """
        Return a list of documents selected based on the given filter.
        @param filter: dict
        @param projection: dict
        @param options: dict
        """
        return self.data_layer.find(self.resource, filter, projection, **options)

    def create(self, docs):
        """
        Insert a list of documents
        @param docs: list
        """
        self.validate(docs)
        self.on_create(docs)
        res = self.data_layer.create(self.resource, docs)
        self.on_created(docs)
        return res

    def update(self, filter, doc, etag=None):
        """
        Update one document selected based on the given filter.
        @param filter: dict
        @param doc: dict
        """
        self.validate(doc)
        orig = self.find_one(filter)
        if not orig:
            raise InvalidFilter(filter, 'update')
        if etag:
            self.validate_etag(orig, etag)
        self.on_update(doc, orig)
        res = self.data_layer.update(self.resource, filter, doc)
        self.on_updated(doc, orig)
        return res

    def replace(self, filter, doc, etag=None):
        """
        Replace the content of one document selected based on the given filter.
        @param filter: dict
        @param doc: dict
        """
        self.validate(doc)
        orig = self.find(filter)
        if orig.count() != 1:
            raise InvalidFilter(filter, 'replace')

        orig = list(orig)

        if etag:
            self.validate_etag(orig, etag)
        self.on_update(doc, orig[0])
        res = self.data_layer.replace(self.resource, filter, doc)
        self.on_updated(doc, orig[0])
        return res

    def delete(self, filter):
        """
        Delete one document selected based on the given filter.
        @param filter: dict
        """
        orig = self.find_one(filter)
        if not orig:
            return
        self.on_delete(orig)
        res = self.data_layer.delete(self.resource, filter)
        self.on_deleted(orig)
        return res

    def validate(self, docs):
        """
        Validate a document or a list of documents.
        Raise ValidationError on errors
        @param docs: list of documents
        """
        errs = []
        if not isinstance(docs, list):
            docs = [docs]
        for doc in docs:
            err = self.validator.validate(doc)
            if errs:
                errs.append(err)
        if errs:
            raise ValidationError(errs)
