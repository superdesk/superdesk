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
                    return isOK(response) ? response : $q.reject(response);
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
            Resource.prototype.url = function() {
                return this.parent ? urls.item(this.parent._links.self.href) + '/' + this.resource : urls.resource(this.resource);
            };

            /**
             * Save an item
             */
            Resource.prototype.save = function(item, diff) {
                return http({
                    method: item._links ? 'PATCH' : 'POST',
                    url: item._links ? urls.item(item._links.self.href) : this.url(),
                    data: diff ? diff : clean(item)
                }).then(function(response) {
                    angular.extend(item, diff || {});
                    angular.extend(item, response.data);
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
                }).then(function(response) {
                    return response.data;
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
