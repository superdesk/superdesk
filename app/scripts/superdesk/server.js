define([
    'angular',
    'restangular'
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
            _clean: function(item) {
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
                    var items = datas;
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
                    console.log(response);
                    delay.resolve(response);
                });

                return delay.promise;
            },
            create: function(resource, data) {},
            createAll: function(resource, datas) {},
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
            readAll: function(items) {
                return this._all('read', items);
            },
            update: function(item) {
                var delay = $q.defer();

                $http({
                    method: 'PATCH',
                    url: this._wrapUrl(item._links.self.href),
                    data: this._clean(item),
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
            },
            updateAll: function(items) {
                return this._all('update', items);
            },
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
            },
            deleteAll: function(items) {
                return this._all('delete', items);
            }
        };

        return server;
    });
});