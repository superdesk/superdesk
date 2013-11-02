define([
    'superdesk-auth/authService',
    'superdesk/services/storage',
    'superdesk/server',
    'angular-mocks'
], function(authService) {
    'use strict';

    beforeEach(function() {
        module('superdesk.services.storage');
        module('superdesk.server');
        module('ngMock');
    });

    describe('AuthService', function() {
        var service, rootScope, storage, server, httpBackend;

        beforeEach(inject(function($injector, $rootScope, $http, $q, $httpBackend, _storage_, _server_) {
            storage = _storage_;
            storage.clear();

            server = _server_;

            rootScope = $rootScope.$new();
            service = {};

            httpBackend = $httpBackend;

            $injector.invoke(authService, service, {
                '$rootScope': rootScope,
                '$http': $http,
                '$q': $q,
                'server': server,
                'storage': storage
            });
        }));

        it('can login and logout', function() {
            expect(service.hasIdentity()).toBe(false);
            expect(rootScope.currentUser.isAnonymous).toBe(true);

            httpBackend
                .expectPOST('http://localhost/auth', {data: {username: 'foo', password: 'bar'}})
                .respond(200, {data: {token: 'x', user: {username:'foo'}}});
            service.login('foo', 'bar');
            httpBackend.flush();

            expect(service.hasIdentity()).toBe(true);
            expect(rootScope.currentUser.isAnonymous).toBe(false);
            expect(rootScope.currentUser.username).toBe('foo');

            service.logout();

            expect(service.hasIdentity()).toBe(false);
        });

        it('fails on false login', function() {
            expect(service.hasIdentity()).toBe(false);

            httpBackend
                .expectPOST('http://localhost/auth', {data: {username: 'fake', password: 'bar'}})
                .respond(400);
            service.login('fake', 'bar');
            httpBackend.flush();
            
            expect(service.hasIdentity()).toBe(false);
        });
    });
});
