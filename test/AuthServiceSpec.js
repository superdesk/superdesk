define([
    'superdesk/auth/authService',
    'angular-mocks'
], function(authService) {
    'use strict';

    describe('Injector', function() {
        var injector;

        beforeEach(inject(function($injector) {
            injector = $injector;
        }));

        it('is injector', function() {
            expect(typeof injector).toBe('object');
            expect(typeof injector.invoke).toBe('function');
        });
    });

    describe('AuthService', function() {
        var service, rootScope;

        beforeEach(inject(function($injector, $rootScope, $http, $q) {
            rootScope = $rootScope.$new();
            service = {};
            $injector.invoke(authService, service, {
                '$rootScope': rootScope,
                '$http': $http,
                '$q': $q,
                'Auth': null
            });
        }));

        it('hasIdentity', function() {
            expect(service.hasIdentity()).toBe(false);
        });
    });
});
