define([
    'superdesk-auth/authService',
    'superdesk/services/storage',
    'superdesk/entity',
    'superdesk/server',
    'angular-mocks'
], function(authService) {
    'use strict';

    beforeEach(function() {
        module('superdesk.services');
        module('ngMock');
    });

    describe('AuthService', function() {
        var service, rootScope, storage, httpBackend;

        beforeEach(inject(function($injector, $rootScope, $http, $q, $httpBackend, _storage_, em) {
            storage = _storage_;
            storage.clear();

            rootScope = $rootScope.$new();
            service = {};

            httpBackend = $httpBackend;

            $injector.invoke(authService, service, {
                '$rootScope': rootScope,
                '$http': $http,
                '$q': $q,
                'em': em,
                'storage': storage
            });
        }));

        it('can login and logout', function() {
            expect(service.hasIdentity()).toBe(false);
            expect(rootScope.currentUser.isAnonymous).toBe(true);

            httpBackend
                .expectPOST('http://localhost/auth', {username: 'foo', password: 'bar'})
                .respond(200, {token: 'x', user: '123abc'});
            httpBackend
                .expectGET('http://localhost/users/123abc')
                .respond(200, {_id: '123abc', username: 'foo'});
            service.login('foo', 'bar');
            httpBackend.flush();

            expect(service.hasIdentity()).toBe(true);
            expect(service.getIdentity()).toBe('123abc');
            expect(rootScope.currentUser.isAnonymous).toBe(false);
            expect(rootScope.currentUser.username).toBe('foo');

            service.logout();

            expect(service.hasIdentity()).toBe(false);
        });

        it('fails on false login', function() {
            expect(service.hasIdentity()).toBe(false);

            httpBackend
                .expectPOST('http://localhost/auth', {username: 'fake', password: 'bar'})
                .respond(400);
            service.login('fake', 'bar');
            httpBackend.flush();
            
            expect(service.hasIdentity()).toBe(false);
        });
    });
});
