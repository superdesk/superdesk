define([
    'angular'
], function(angular) {
    'use strict';

    angular.module('superdesk.server', [])
    .service('server', function($q, $http) {

        var server = {
            _makeUrl: function(resource) {
                return ServerConfig.url + '/' + resource;
            },
            _wrapUrl: function(url) {
                if (ServerConfig.url.indexOf('https') === 0) {
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
                var delay = $q.defer();

                var data = this._cleanData(data);

                $http({
                    method: 'POST',
                    url: this._makeUrl(resource),
                    data: {data: data},
                    cache: true
                })
                .success(function(data, status, headers, config) {
                    delay.resolve(data.data);
                })
                .error(function(data, status, headers, config) {
                    delay.reject(data);
                });

                return delay.promise;
            },
            /**
             * List items
             *
             * @param {string} resource
             * @param {Object} params
             * @return {Object} promise
             */
            list: function(resource, params) {
                var delay = $q.defer();

                $http({
                    method: 'GET',
                    url: this._makeUrl(resource),
                    params: params,
                    cache: true
                })
                .success(function(data, status, headers, config) {
                    delay.resolve(data);
                })
                .error(function(data, status, headers, config) {
                    delay.reject(data);
                });

                return delay.promise;
            },
            /**
             * Read single item
             *
             * @param {Object} item
             * @return {Object} promise
             */
            read: function(item) {
                var delay = $q.defer();

                $http({
                    method: 'GET',
                    url: this._wrapUrl(item._links.self.href),
                    cache: true
                })
                .success(function(data, status, headers, config) {
                    delay.resolve(data);
                })
                .error(function(data, status, headers, config) {
                    delay.reject(data);
                });

                return delay.promise;
            },
            /**
             * Update single item
             *
             * @param {Object} item
             * @return {Object} promise
             */
            update: function(item) {
                var delay = $q.defer();

                var created = item.created;
                var data = this._cleanData(item);

                $http({
                    method: 'PATCH',
                    url: this._wrapUrl(item._links.self.href),
                    data: {data: data},
                    headers: {'If-Match': item.etag},
                    cache: true
                })
                .success(function(data, status, headers, config) {
                    var fields = ['_id', '_links', 'etag', 'updated'];
                    _.forEach(fields, function(field) {
                        item[field] = data.data[field];
                    });
                    item.created = created;
                    delay.resolve(item);
                })
                .error(function(data, status, headers, config) {
                    delay.reject(data);
                });

                return delay.promise;
            },
            /**
             * Delete single item
             *
             * @param {Object} item
             * @return {Object} promise
             */
            delete: function(item) {
                var delay = $q.defer();

                $http({
                    method: 'DELETE',
                    url: this._wrapUrl(item._links.self.href),
                    headers: {'If-Match': item.etag},
                    cache: true
                })
                .success(function(data, status, headers, config) {
                    delay.resolve(data);
                })
                .error(function(data, status, headers, config) {
                    delay.reject(data);
                });

                return delay.promise;
            }
        };

        return server;
    });
});