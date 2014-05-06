define(['lodash'], function(_) {
    'use strict';

    /**
     * Http endpoint factory
     */
    HttpEndpointFactory.$inject = ['$http', '$q', 'config'];
    function HttpEndpointFactory($http, $q, config) {

        var links;

        /**
         * Get resource links via root url
         *
         * @returns {Promise}
         */
        function getResourceLinks() {

            if (links) {
                return $q.when(links);
            }

            return http({
                method: 'GET',
                url: config.server.url
            }).then(function(response) {
                links = {};
                _.each(response.data._links.child, function(link) {
                    links[link.title] = 'http://' + link.href;
                });

                return links;
            });
        }

        /**
         * Get url for given resource
         *
         * @param {Object} resource
         * @returns {Promise}
         */
        function getUrl(resource) {
            return getResourceLinks().then(function(links) {
                return links[resource.rel] ? links[resource.rel] : $q.reject(resource);
            });
        }

        /**
         * Get headers for given resource
         *
         * @param {Object} resource
         * @returns {Object}
         */
        function getHeaders(resource) {
            return _.extend({}, resource.config.headers || {});
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
                    if (response.status >= 200 && response.status < 300) {
                        return response;
                    } else {
                        return $q.reject(response);
                    }
                });
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
        HttpEndpoint.prototype.getByUrl = function(url) {
            return http({
                method: 'GET',
                url: url
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
        HttpEndpoint.prototype.getById = function(id) {
            return getUrl(this).then(_.bind(function(resourceUrl) {
                var url = resourceUrl.replace(/\/+$/, '') + '/' + id;
                return this.getByUrl(url);
            }, this));
        };

        /**
         * Resource query method
         *
         * @param {Object} params
         */
        HttpEndpoint.prototype.query = function(params) {
            return http({
                method: 'GET',
                params: params,
                url: getUrl(this),
                headers: getHeaders(this)
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
            if (diff == null) {
                diff = _.omit(item, function(value, key) {
                    return key === 'href' || key === 'Id' || value.href;
                });
            }
            return http({
                method: 'PATCH',
                url: item.href,
                data: diff,
                headers: getHeaders(this)
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
            return item.href ? this.update(item, diff) : this.create(_.extend(item, diff));
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
                url: dest,
                data: item
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
                url: item.href
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
