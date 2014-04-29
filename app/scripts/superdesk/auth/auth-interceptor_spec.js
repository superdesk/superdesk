define([
    './auth-interceptor',
    'superdesk/api/request-service'
], function(AuthInterceptor, RequestService) {
    'use strict';

    describe('auth interceptor', function() {

        beforeEach(module(function($provide) {
            $provide.service('request', RequestService);
        }));

        it('should intercept 401 response, run auth and resend request',
        inject(function($injector, $q, $rootScope, session, request) {

            var interceptor = $injector.invoke(AuthInterceptor),
                config = {method: 'GET', url: 'test', headers: {}},
                response = {status: 401, config: config};

            spyOn(session, 'expire');
            spyOn(session, 'getIdentity').andReturn($q.when());
            spyOn(request, 'resend');

            interceptor.response(response);
            $rootScope.$digest();

            expect(session.expire).toHaveBeenCalled();
            expect(request.resend).toHaveBeenCalled();
        }));

    });
});
