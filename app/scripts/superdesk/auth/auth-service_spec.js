define([
    'angular',
    'superdesk/auth/auth-service'
], function(angular, authService) {
    'use strict';

    var USER_HREF = 'http://user/1',
        SESSION = 'sess',
        USERNAME = 'foo';

    beforeEach(function() {
        localStorage.clear();
        module('superdesk.services');
        module(function($provide) {
            $provide.service('auth', authService);
            $provide.service('authAdapter', AuthAdapterMock);
        });
    });

    describe('auth service from scratch', function() {

        beforeEach(inject(function(auth) {
            auth.logout();
        }));

        it('has no identity on init', inject(function(auth) {
            expect(auth.identity).toBe(null);
        }));

        it('can login', inject(function(auth, $http, $httpBackend, $rootScope) {
            var resolved = {};

            $httpBackend.expectGET(USER_HREF).respond({UserName: USERNAME});

            auth.getIdentity().then(function(identity) {
                expect(identity.UserName).toBe(USERNAME);
                resolved.identity = true;
            });

            auth.login('admin', 'admin').then(function() {
                expect(auth.identity.UserName).toBe(USERNAME);
                expect($rootScope.currentUser.UserName).toBe(USERNAME);
                expect($http.defaults.headers.common.Authorization).toBe(SESSION);
                resolved.login = true;
            });

            $httpBackend.flush();
            $rootScope.$apply();

            expect(resolved.login).toBe(true);
            expect(resolved.identity).toBe(true);
        }));

        it('does not resolve on login failure', inject(function(auth, $rootScope) {
            var resolved = false;
            auth.login('wrong', 'credentials').then(function() {
                resolved = true;
            }, function() {
                resolved = true;
            });

            $rootScope.$apply();
            expect(resolved).toBe(false);
        }));
    });

    describe('auth service with stored identity', function() {
        beforeEach(inject(function(auth, $rootScope, $httpBackend) {
            $httpBackend.expectGET(USER_HREF).respond({UserName: USERNAME});

            auth.login('admin', 'admin');

            $httpBackend.flush();
            $rootScope.$apply();
        }));

        it('can get reuse identity', inject(function(auth, $rootScope, $http) {
            expect(auth.identity.UserName).toBe(USERNAME);
            expect($rootScope.currentUser.UserName).toBe(USERNAME);
            expect($http.defaults.headers.common.Authorization).toBe(SESSION);
        }));

        it('can logout', inject(function(auth, $rootScope, $http) {
            auth.logout();
            expect(auth.identity).toBe(null);
            expect($rootScope.currentUser).toBe(null);
            expect($http.defaults.headers.common.Authorization).toBe(undefined);
        }));
    });

    /**
     * Mock auth adapter which will authenticate admin:admin and fail otherwise
     */
    function AuthAdapterMock($q) {

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
    }
});
