define([
    './timeout-interceptor',
    './request-service'
], function(TimeoutHttpInterceptor, RequestService) {
    'use strict';

    describe('timeout http interceptor', function() {
        var service;

        beforeEach(module(function($provide) {
            $provide.service('request', RequestService);
            $provide.service('upload', function() {
                this.isUpload = function() {
                    return false;
                };
            });
        }));

        beforeEach(inject(function($injector) {
            service = $injector.invoke(TimeoutHttpInterceptor);
        }));

        xit('monitors requests and stop them after while', inject(function($rootScope) {
            var config = {
                method: 'GET',
                url: 'test'
            };

            expect($rootScope.serverStatus).toBe(0);

            expect(service.request(config)).toBe(config);
            expect(config.timeout).toBeTruthy();

            service.responseError({
                status: null,
                config: config
            });

            expect($rootScope.serverStatus).toBe(1);

            service.responseError({
                status: null,
                config: config
            });

            expect($rootScope.serverStatus > 1).toBe(true);

            service.response({
                status: 200,
                config: config
            });

            expect($rootScope.serverStatus).toBe(0);

            service.request(config);

            service.responseError({status: null, config: config});
            service.responseError({status: 400, config: config});
            expect($rootScope.serverStatus).toBe(0);
        }));

    });
});
