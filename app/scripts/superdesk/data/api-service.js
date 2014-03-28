define([
    'lodash',
    './mock-endpoint-factory',
    './http-endpoint-factory'
], function(_, MockEndpointFactory, HttpEndpointFactory) {
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

        apiServiceFactory.$inject = ['$injector'];
        function apiServiceFactory($injector) {

            var endpoints = {
                'mock': $injector.invoke(MockEndpointFactory),
                'http': $injector.invoke(HttpEndpointFactory)
            };

            return _.mapValues(apis, function(config, apiName) {
                var service = config.service || _.noop;
                service.prototype = new endpoints[config.type](apiName, config.backend);
                return $injector.instantiate(service, {resource: service.prototype});
            });
        }
    }

    return APIProvider;
});
