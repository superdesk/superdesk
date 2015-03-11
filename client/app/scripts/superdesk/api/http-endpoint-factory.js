define(['lodash'], function(_) {
    'use strict';

    /**
     * Http endpoint factory
     */
    HttpEndpointFactory.$inject = ['$http', '$q', 'urls'];
    function HttpEndpointFactory($http, $q, urls) {

        /**
         * Get url for given resource
         *
         * @param {Object} resource
         * @returns {Promise}
         */
        function getUrl(resource) {
            return urls.resource(resource.rel);
        }

        /**
         * Get headers for given resource
         *
         * @param {Object} resource
         * @param {Object} item
         * @returns {Object}
         */
        function getHeaders(resource, item) {
            var headers = _.extend({}, resource.config.headers || {});
            if (item && item._etag) {
                headers['If-Match'] = item._etag;
            }
            return headers;
        }

        /**
         * Wrap $http call
         *
         * @param {Object} config
         * @returns {Promise}
         */
        function http(config) {
            return $q.when(config.url)
                .then(function(url) {
                    config.url = url;
                    return $http(config);
                })
                .then(function(response) {
                    if (response.status >= 200 && response.status < 300 &&
                    (!response.data || !response.data._status || response.data._status !== 'ERR')) {
                        return response;
                    } else {
                        return $q.reject(response);
                    }
                });
        }

        /**
         * Remove keys prefixed with '_'
         */
        function clean(data, keepId) {
            var blacklist = {
                    _status: 1,
                    _updated: 1,
                    _created: 1,
                    _etag: 1,
                    _links: 1,
                    _id: keepId ? 0 : 1
                },
                cleanData = {};

            angular.forEach(data, function(val, key) {
                if (!blacklist[key]) {
                    cleanData[key] = val;
                }
            });

            return cleanData;
        }

        /**
         * Http Endpoint
         */
        function HttpEndpoint(name, config) {
            this.name = name;
            this.config = config;
            this.rel = config.rel;
        }

        /**
         * Get entity by url
         *
         * @param {string} url
         * @returns {Promise}
         */
        HttpEndpoint.prototype.getByUrl = function(url, cache) {
            return http({
                method: 'GET',
                url: urls.item(url),
                cache: cache
            }).then(function(response) {
                return response.data;
            });
        };

        /**
         * Get entity by given id
         *
         * @param {string} id
         * @returns {Promise}
         */
        HttpEndpoint.prototype.getById = function(id, cache) {
            return getUrl(this).then(_.bind(function(resourceUrl) {
                var url = resourceUrl.replace(/\/+$/, '') + '/' + id;
                return http({
                    method: 'GET',
                    url: url,
                    cache: cache
                }).then(function(response) {
                    return response.data;
                });
            }, this));
        };

        /**
         * Resource query method
         *
         * @param {Object} params
         */
        HttpEndpoint.prototype.query = function(params, cache) {
            return http({
                method: 'GET',
                params: params,
                url: getUrl(this),
                headers: getHeaders(this),
                cache: cache
            }).then(function(response) {
                return response.data;
            });
        };

        /**
         * Update item
         *
         * @param {Object} item
         * @param {Object} diff
         * @returns {Promise}
         */
        HttpEndpoint.prototype.update = function(item, diff) {
            if (diff && diff._etag) {
                item._etag = diff._etag;
            }

            if (!diff) {
                diff = angular.extend({}, item);
            }

            var url = item._links.self.href;
            return http({
                method: 'PATCH',
                url: urls.item(url),
                data: clean(diff, !item._links),
                headers: getHeaders(this, item)
            }).then(function(response) {
                _.extend(item, response.data);
                return item;
            });
        };

        /**
         * Create new item
         *
         * @param {Object} itemData
         * @returns {Promise}
         */
        HttpEndpoint.prototype.create = function(itemData) {
            return http({
                method: 'POST',
                url: getUrl(this),
                data: itemData,
                headers: getHeaders(this)
            }).then(function(response) {
                delete response.data._status;
                _.extend(itemData, response.data);
                return itemData;
            });
        };

        /**
         * Save item
         *
         * @param {Object} item
         * @param {Object} diff
         * @returns {Promise}
         */
        HttpEndpoint.prototype.save = function(item, diff) {
            return item._id ? this.update(item, diff) : this.create(_.extend(item, diff));
        };

        /**
         * Replace item
         *
         * @param {Object} dest
         * @param {Object} item
         * @returns {Promise}
         */
        HttpEndpoint.prototype.replace = function(dest, item) {
            return http({
                method: 'PUT',
                url: urls.item(dest),
                data: item,
                headers: getHeaders(this, item)
            }).then(function(response) {
                _.extend(item, response.data);
                return item;
            });
        };

        /**
         * Remove item
         *
         * @param {Object} item
         * @returns {Promise}
         */
        HttpEndpoint.prototype.remove = function(item) {
            return http({
                method: 'DELETE',
                url: urls.item(item._links.self.href),
                headers: getHeaders(this, item)
            }).then(null, function(response) {
                return response.status === 404 ? $q.when(response) : $q.reject(response);
            });
        };

        /**
         * Get resource url
         *
         * @returns {Promise}
         */
        HttpEndpoint.prototype.getUrl = function() {
            return getUrl(this);
        };

        /**
         * Get headers
         *
         * @return {Object}
         */
        HttpEndpoint.prototype.getHeaders = function() {
            return getHeaders(this) || {};
        };

        return HttpEndpoint;
    }

    return HttpEndpointFactory;
});
