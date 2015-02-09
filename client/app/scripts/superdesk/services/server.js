define([
    'lodash',
    'angular'
], function(_, angular) {
    'use strict';

    return angular.module('superdesk.services.server', [])
    .service('server', ['$q', '$http', 'config', function($q, $http, config) {
        return {
            _makeUrl: function() {
                var url = config.server.url;
                for (var i = 0; i < arguments.length; i++) {
                    url += '/' + arguments[i];
                }

                return url;
            },

            _wrapUrl: function(url) {
                if (config.server.url.indexOf('https') === 0) {
                    return 'https://' + url;
                } else {
                    return 'http://' + url;
                }
            },
            _cleanData: function(item) {
                var data = _.cloneDeep(item);
                var fields = ['_id', '_links', 'etag', 'updated', 'created'];
                _.forEach(fields, function(field) {
                    delete data[field];
                });
                return data;
            },
            _all: function(functionName, items, datas) {
                var self = this;
                var delay = $q.defer();

                // to make it usable with createAll
                if (datas !== undefined) {
                    var resource = items;
                    items = datas;
                }

                var promises = [];
                _.forEach(items, function(item) {
                    if (resource !== undefined) {
                        promises.push(self[functionName](resource, item));
                    } else {
                        promises.push(self[functionName](item));
                    }
                });

                $q.all(promises).then(function(response) {
                    delay.resolve(response);
                });

                return delay.promise;
            },
            _http: function(method, url, params, data) {
                var delay = $q.defer();

                method = method.toLowerCase();
                var options = {
                    method: method,
                    url: url,
                    params: params,
                    cache: false
                };

                if (method === 'patch') {
                    var created = data.created;
                }
                if (method === 'delete' || method === 'patch') {
                    options.headers = {'If-Match': data.etag};
                }
                if (method === 'post' || method === 'patch') {
                    options.data = this._cleanData(data);
                }

                $http(options)
                .success(function(responseData) {
                    if (method === 'post') {
                        delay.resolve(responseData);
                    } else if (method === 'patch') {
                        var fields = ['_id', '_links', 'etag', 'updated'];
                        _.forEach(fields, function(field) {
                            data[field] = responseData[field];
                        });
                        data.created = created;
                        delay.resolve(data);
                    } else {
                        delay.resolve(responseData);
                    }
                })
                .error(function(responseData) {
                    delay.reject(responseData);
                });

                return delay.promise;
            },
            /**
             * Create multiple items
             *
             * @param {string} resource
             * @param {Array} datas
             * @return {Array} promise
             */
            createAll: function(resource, datas) {
                return this._all('create', resource, datas);
            },
            /**
             * Read multiple items
             *
             * @param {Array} items
             * @return {Array} promise
             */
            readAll: function(items) {
                return this._all('read', items);
            },
            /**
             * Update multiple items
             *
             * @param {Array} items
             * @return {Array} promise
             */
            updateAll: function(items) {
                return this._all('update', items);
            },
            /**
             * Delete multiple items
             *
             * @param {Array} items
             * @return {Array} promise
             */
            deleteAll: function(items) {
                return this._all('delete', items);
            },
            /**
             * Create single item
             *
             * @param {string} resource
             * @param {Object} data
             * @return {Object} promise
             */
            create: function(resource, data) {
                return this._http('post',
                    this._makeUrl(resource),
                    null,
                    data
                );
            },
            /**
             * List items
             *
             * @param {string} resource
             * @param {Object} params
             * @return {Object} promise
             */
            list: function(resource, params) {
                return this._http('get',
                    this._makeUrl(resource),
                    this._convertParams(params)
                );
            },

            // transfer url params to server params
            _convertParams: function(params) {
                var serverParams = _.extend({}, _.pick(params, ['filter', 'max_results', 'page', 'embedded', 'where', 'q', 'df']));

                if ('sort' in params) {
                    serverParams.sort = '[(' + angular.toJson(params.sort[0]) + ',' + (params.sort[1] === 'asc' ? 1 : -1) + ')]';
                }

                if ('perPage' in params) {
                    serverParams.max_results = params.perPage;
                }

                if (params.search) {
                    var search = {};
                    search[params.searchField] = params.search;
                    angular.extend(serverParams.where, search);
                }

                return serverParams;
            },

            /**
             * Read single item
             *
             * @param {Object} item
             * @return {Object} promise
             */
            read: function(item) {
                return this._http('get',
                    this._wrapUrl(item._links.self.href)
                );
            },

            /**
             * Read single item by given id
             *
             * @param {string} resource
             * @param {string} id
             * @return {Object} promise
             */
            readById: function(resource, id) {
                return this._http('get',
                    this._makeUrl(resource, id)
                );
            },

            /**
             * Update single item
             *
             * @param {Object} item
             * @param {Object} data to be updated, if not provided will send item data
             * @return {Object} promise
             */
            update: function(item, data) {
                if (data) {
                    data._id = item._id;
                    data.created = item.created;
                    data.updated = item.updated;
                    data.etag = item.etag;
                }

                return this._http('patch',
                    this._wrapUrl(item._links.self.href),
                    {},
                    item
                );
            },
            /**
             * Delete single item
             *
             * @param {Object} item
             * @return {Object} promise
             */
            'delete': function(item) {
                return this._http('delete',
                    this._wrapUrl(item._links.self.href),
                    {},
                    item
                );
            }
        };
    }]);
});
