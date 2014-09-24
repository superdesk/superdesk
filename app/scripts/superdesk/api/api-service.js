define([
    'angular',
    './http-endpoint-factory'
], function(angular, HttpEndpointFactory) {
    'use strict';

    /**
     * Api layer provider
     */
    function APIProvider() {
        var apis = {};

        /**
         * Register an api
         */
        this.api = function(name, config) {
            apis[name] = config;
            return this;
        };

        this.$get = apiServiceFactory;

        apiServiceFactory.$inject = ['$injector', '$q', '$http', 'urls'];
        function apiServiceFactory($injector, $q, $http, urls) {

            var endpoints = {
                'http': $injector.invoke(HttpEndpointFactory)
            };

            function isOK(response) {

                function isErrData(data) {
                    return data && data._status && data._status === 'ERR';
                }

                return response.status >= 200 && response.status < 300 && !isErrData(response.data);
            }

            /**
             * Call $http once url is resolved
             */
            function http(config) {
                return $q.when(config.url).then(function(url) {
                    config.url = url;
                    return $http(config);
                }).then(function(response) {
                    return isOK(response) ? response.data : $q.reject(response);
                });
            }

            /**
             * Remove keys prefixed with '_'
             */
            function clean(data) {
                return _.omit(data, function(val, key) {
                    return angular.isString(key) && key[0] === '_';
                });
            }

            /**
             * API Resource instance
             */
            function Resource(resource, parent) {
                this.resource = resource;
                this.parent = parent;
            }

            /**
             * Get resource url
             */
            Resource.prototype.url = function(_id) {

                function resolve(urlTemplate, data) {
                    return urlTemplate.replace(/<.*>/, data._id);
                }

                return urls.resource(this.resource)
                    .then(angular.bind(this, function(url) {
                        if (this.parent) {
                            url = resolve(url, this.parent);
                        }

                        if (_id) {
                            url = url + '/' + _id;
                        }

                        return url;
                    }));
            };

            /**
             * Save an item
             */
            Resource.prototype.save = function(item, diff, params) {
                return http({
                    method: item._links ? 'PATCH' : 'POST',
                    url: item._links ? urls.item(item._links.self.href) : this.url(),
                    data: diff ? diff : clean(item),
                    params: params
                }).then(function(data) {
                    angular.extend(item, diff || {});
                    angular.extend(item, data);
                    return item;
                });
            };

            /**
             * Query resource
             */
            Resource.prototype.query = function(params) {
                return http({
                    method: 'GET',
                    url: this.url(),
                    params: params
                });
            };

            /**
             * Get an item by _id
             *
             * @param {String} _id
             */
            Resource.prototype.getById = function(_id, params) {
                return http({
                    method: 'GET',
                    url: this.url(_id),
                    params: params
                });
            };

            /**
             * Remove an item
             *
             * @param {Object} item
             */
            Resource.prototype.remove = function(item, params) {
                return http({
                    method: 'DELETE',
                    url: urls.item(item._links.self.href),
                    params: params
                });
            };

            // api service
            var api = function apiService(resource, parent) {
                return new Resource(resource, parent);
            };

            angular.forEach(apis, function(config, apiName) {
                var service = config.service || _.noop;
                service.prototype = new endpoints[config.type](apiName, config.backend);
                api[apiName] = $injector.instantiate(service, {resource: service.prototype});
            });

            return api;
        }
    }

    return APIProvider;
});
