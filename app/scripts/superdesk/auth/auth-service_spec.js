define([
    'superdesk/auth/auth-service'
], function(authService) {
    'use strict';

    var USER_HREF = 'http://user/1',
        SESSION = 'sess';

    var testModule = angular.module('test.auth.service', [])
        .service('auth', authService)
        .factory('storage', function() { return sessionStorage; })
        .service('authAdapter', function($q) {

            /**
             * Mock auth - authenticate with admin:admin
             */
            this.authenticate = function(username, password) {
                var defer = $q.defer();

                if (username === 'admin' && password === 'admin') {
                    defer.resolve({Session: SESSION, User: {href: USER_HREF}});
                } else {
                    defer.reject();
                }

                return defer.promise;
            };
        });

    describe('auth service', function() {

        beforeEach(function() {
            module('superdesk.services');
            module(testModule.name);
            sessionStorage.removeItem('auth:token');
        });

        it('has no identity on init', inject(function(auth) {
            expect(auth.identity).toBe(null);
        }));

        it('can login and logout', inject(function(auth, $http, $httpBackend, $rootScope) {
            $httpBackend.expectGET(USER_HREF).respond({UserName: 'foo'});

            var resolved = {};
            auth.getIdentity().then(function(identity) {
                expect(identity.UserName).toBe('foo');
                expect(!!auth.identity).toBe(true);
                resolved.identity = true;
            });

            auth.login('admin', 'admin').then(function() {
                expect(!!auth.identity).toBe(true);
                expect(auth.identity.UserName).toBe('foo');
                expect($http.defaults.headers.common.Authorization).toBe(SESSION);
                resolved.login = true;
            }).then(function() {
                auth.logout();
                expect(auth.identity).toBe(null);
                resolved.logout = true;
            });

            $httpBackend.flush();
            $rootScope.$apply();
            expect(resolved.login).toBe(true);
            expect(resolved.identity).toBe(true);
            expect(resolved.logout).toBe(true);
        }));

        it('fails login with wrong credentials', inject(function(auth) {
            expect(auth.identity).toBe(null);

            auth.login('foo', 'foo').then(function() {
                expect(auth.identity).toBe(null);
            });
        }));
    });

    describe('auth service init', function() {
        beforeEach(function() {
            module('superdesk.services');
            module(testModule.name);
            sessionStorage.setItem('auth:token', 'sess');
            sessionStorage.setItem('auth:user', 'http://localhost/HR/User/1');
        });

        afterEach(inject(function($httpBackend) {
            $httpBackend.verifyNoOutstandingExpectation();
            $httpBackend.verifyNoOutstandingRequest();
        }));

        it('can get saved identity', inject(function(auth, $q, $rootScope, $httpBackend) {
            var resolved = false;

            $httpBackend
                .expectGET(sessionStorage.getItem('auth:user'))
                .respond({UserName: 'foo'});

            auth.getIdentity().then(function(identity) {
                resolved = true;
                expect(!!auth.identity).toBe(true);
                expect(auth.identity.UserName).toBe('foo');
            });

            $httpBackend.flush();
            $rootScope.$apply();
            expect(resolved).toBe(true);
        }));
    });
});
