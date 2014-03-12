define(['angular', 'superdesk/data/timeout-interceptor'], function(angular, TimeoutHttpInterceptor) {
    'use strict';

    describe('timeout http interceptor', function() {
        var service;

        beforeEach(inject(function($injector) {
            service = $injector.invoke(TimeoutHttpInterceptor);
        }));

        it('monitors requests and stop them after while', inject(function($rootScope) {
            var config = {
                method: 'GET',
                url: 'test'
            };

            expect($rootScope.serverStatus).toBe(0);

            expect(service.request(config)).toBe(config);
            expect(config.timeout > 0).toBe(true);

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
            expect(service.responseError({status: 400, config: config}).status).toBe(400);
            expect($rootScope.serverStatus).toBe(0);
        }));

    });
});
