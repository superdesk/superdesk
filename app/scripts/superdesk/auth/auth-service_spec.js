define([
    'superdesk/services/storage',
    'superdesk/auth/auth-service',
    'superdesk/auth/session-service'
], function(StorageService, AuthService, SessionService) {
    'use strict';

    var USER_HREF = 'http://user/1',
        SESSION = 'sess',
        USERNAME = 'foo';

    beforeEach(function() {
        module(StorageService.name);
        module(function($provide) {
            $provide.service('auth', AuthService);
            $provide.service('session', SessionService);
            $provide.service('authAdapter', AuthAdapterMock);
        });
    });

    describe('auth service', function() {
        beforeEach(inject(function(session) {
            session.clear();
        }));

        it('can login', inject(function(auth, session, $httpBackend, $rootScope) {

            expect(session.identity).toBe(null);
            expect(session.token).toBe(null);

            var resolved = {};

            $httpBackend.expectGET(USER_HREF).respond({UserName: USERNAME});

            session.getIdentity().then(function() {
                resolved.identity = true;
            });

            auth.login('admin', 'admin').then(function(identity) {
                expect(session.identity.UserName).toBe(USERNAME);
                expect(session.token).toBe(SESSION);
                resolved.login = true;
            });

            $httpBackend.flush();
            $rootScope.$apply();

            expect(resolved.login).toBe(true);
            expect(resolved.identity).toBe(true);
        }));

        it('checks credentials', inject(function(auth, $rootScope) {
            var resolved = false, rejected = false;

            auth.login('wrong', 'credentials').then(function() {
                resolved = true;
            }, function() {
                rejected = true;
            });

            $rootScope.$apply();
            expect(resolved).toBe(false);
            expect(rejected).toBe(true);
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
