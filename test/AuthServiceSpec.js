define([
    'superdesk/auth/authService',
    'superdesk/storage',
    'angular-mocks'
], function(authService) {
    'use strict';

    beforeEach(function() {
        module('superdesk.storage');
    });

    describe('AuthService', function() {
        var service, rootScope, auth, authData, storage;

        beforeEach(inject(function($injector, $rootScope, $http, $q, _storage_) {
            storage = _storage_;
            storage.clear();

            rootScope = $rootScope.$new();
            service = {};

            authData = {
                'token': 'abc',
                'user': {'username': 'foo'}
            };

            auth = {
                save: function(data, success, error) {
                    if (data.username == 'foo') {
                        success(authData);
                    } else {
                        error(data);
                    }
                }
            };

            $injector.invoke(authService, service, {
                '$rootScope': rootScope,
                '$http': $http,
                '$q': $q,
                'Auth': auth,
                'storage': storage
            });
        }));

        it('can login and logout', function() {
            expect(service.hasIdentity()).toBe(false);
            expect(rootScope.currentUser.isAnonymous).toBe(true);

            service.login('foo', 'bar');

            expect(service.hasIdentity()).toBe(true);
            expect(rootScope.currentUser.isAnonymous).toBe(false);
            expect(rootScope.currentUser.username).toBe(authData.user.username);

            service.logout();

            expect(service.hasIdentity()).toBe(false);
        });

        it('fails on false login', function() {
            service.login('fake', 'bar');
            
            expect(service.hasIdentity()).toBe(false);
        });
    });
});
