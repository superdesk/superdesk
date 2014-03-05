define(['lodash'], function(_) {
    'use strict';

    /**
     * Resource service provider
     */
    function ResourceServiceProvider() {

        var resources = {};

        this.resource = function(name, config) {
            resources[name] = config;
        };

        this.$get = ['$http', '$q', 'config', function($http, $q, config) {
            var service = new ResourceService($http, $q, config);
            registerResources(service);
            return service;
        }];

        function registerResources(service) {
            _.each(resources, function(config, name) {
                service.resource(name, config);
            });
        }
    }

    /**
     * Resource service
     */
    function ResourceService($http, $q, config) {

        /**
         * Register resource
         *
         * @param {string} name
         * @param {Object} config
         * @returns {ResourceService}
         */
        this.resource = function(name, config) {
            this[name] = new Resource(config);
        };

        /**
         * Get root url for given resource
         *
         * @param {Object} resource
         * @returns {Promise}
         */
        function getUrl(resource) {
            return $http.get(config.server.url, {cache: true})
                .then(function(response) {
                    if (response.status === 200 && response.data) {
                        var link = _.find(response.data.collection, {rel: resource.rel});
                        if (link && link.href) {
                            return link.href;
                        }
                    }

                    $q.reject(response);
                });
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
         * Resource wrapper
         */
        function Resource(config) {
            this.rel = config.rel;
        }

        /**
         * Get url
         *
         * @return {Promise}
         */
        Resource.prototype.getUrl = function() {
            return getUrl(this);
        };

        /**
         * Resource query method
         *
         * @param {Object} params
         */
        Resource.prototype.query = function(params) {
            return http({
                method: 'GET',
                params: params,
                url: this.getUrl()
            }).then(function(response) {
                response.data._items = response.data.collection;
                return response.data;
            });
        };

        /**
         * Update item
         *
         * @param {Object} item
         * @returns {Promise}
         */
        Resource.prototype.update = function(item) {
            var url = item.href;
            delete item.href;
            return http({
                method: 'PATCH',
                url: url,
                data: item
            }).then(function(response) {
                _.extend(item, {href: url}, response.data);
                return item;
            });
        };

        /**
         * Create new item
         *
         * @param {Object} itemData
         * @returns {Promise}
         */
        Resource.prototype.create = function(itemData) {
            return http({
                method: 'POST',
                data: itemData,
                url: this.getUrl()
            }).then(function(response) {
                _.extend(itemData, response.data);
                return itemData;
            });
        };

        /**
         * Save item
         *
         * @param {Object} item
         * @returns {Promise}
         */
        Resource.prototype.save = function(item) {
            return item.href ? this.update(item) : this.create(item);
        };

        /**
         * Delete item
         *
         * @param {Object} item
         * @returns {Promise}
         */
        Resource.prototype['delete'] = function(item) {
            return http({
                method: 'DELETE',
                url: item.href
            });
        };

        /**
         * Remove item - alias for delete
         */
        Resource.prototype.remove = Resource.prototype['delete'];
    }

    return ResourceServiceProvider;
});
