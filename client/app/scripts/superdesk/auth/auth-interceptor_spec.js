(function() {

    'use strict';

    describe('auth interceptor', function() {

        beforeEach(module('superdesk.api'));
        beforeEach(module('superdesk.auth'));
        beforeEach(module('superdesk.session'));

        it('should intercept 401 response, run auth and resend request',
        inject(function($injector, $q, $rootScope, session, request, AuthExpiredInterceptor) {

            var interceptor = AuthExpiredInterceptor,
                config = {method: 'GET', url: 'http://localhost:5000/test', headers: {}},
                response = {status: 401, config: config};

            spyOn(session, 'expire');
            spyOn(session, 'getIdentity').and.returnValue($q.when());
            spyOn(request, 'resend');

            interceptor.responseError(response);
            $rootScope.$digest();

            expect(session.expire).toHaveBeenCalled();
            expect(request.resend).toHaveBeenCalled();
        }));

        it('should intercept 401 response and reject the request if payload has credentials 1',
        inject(function($injector, $q, $rootScope, session, request, AuthExpiredInterceptor) {

            var interceptor = AuthExpiredInterceptor,
                config = {method: 'POST', url: 'http://localhost:5000/auth', headers: {}},
                response = {status: 401, config: config, data: {_issues: {credentials: 1}}};

            spyOn(session, 'expire');
            spyOn(session, 'getIdentity').and.returnValue($q.when());
            spyOn(request, 'resend');

            var result;
            interceptor.responseError(response).then(function(success) {
                result = success;
            }, function(rejection) {
                result = rejection;
            });

            $rootScope.$digest();
            expect(result.data._issues.credentials).toBe(1);
            expect(session.expire).not.toHaveBeenCalled();
            expect(request.resend).not.toHaveBeenCalled();
        }));
    });
})();
