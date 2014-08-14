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
                return response.status >= 200 && response.status < 300 && !isErrData(response.data);
            }

            function isErrData(data) {
                return data && data._status && data._status === 'ERR';
            }

            function http(config) {
                return $q.when(config.url).then(function(url) {
                    config.url = url;
                    return $http(config);
                }).then(function(response) {
                    return isOK(response) ? response : $q.reject(response);
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
                    method: item._id ? 'PATCH' : 'POST',
                    url: this.url(),
                    data: diff ? diff : item
                }).then(function(response) {
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
