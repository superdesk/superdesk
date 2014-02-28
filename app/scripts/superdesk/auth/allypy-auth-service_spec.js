define([
    'superdesk/auth/allypy-auth-service'
], function(AuthAdapterService) {
    'use strict';

    /* jshint maxlen:false */
    var SERVER_URL = 'http://localhost/resource',
        TOKEN_URL = SERVER_URL + '/Security/Authentication',
        LOGIN_URL = SERVER_URL + '/Security/Login',
        username = 'admin',
        password = 'a',
        token = '07e4f625f5e8f5e380b181a5f8816dfb75418dcbe1c9da4d225895ae37bcaf20507c15e0f78f183e25debe30ba81df1e09e379b493aec02dc194fde73e9fc71e',
        hashedToken = 'bc6adf5c3d7367a4ae4ce3ef6abe6024cd327f5d3ddaadff400d146126a16f96e4ae763a1bf1a858dad4701fecc35f73785cc397ac54487d30da3313a0d7e5f4',
        session = 'xyz';

    describe('allypy auth adapter', function() {
        beforeEach(function() {
            module(function($provide) {
                $provide.value('config', {server: {url: SERVER_URL}});
                $provide.service('authAdapter', AuthAdapterService);
            });
        });

        it('can login', inject(function(authAdapter, $httpBackend) {
            $httpBackend
                .expectPOST(TOKEN_URL).respond(201, {Token: token});

            $httpBackend
                .expectPOST(LOGIN_URL, {UserName: username, Token: token, HashedToken: hashedToken})
                    .respond({Session: session, User: {href: 'user'}});

            var resolved;
            authAdapter.authenticate(username, password).then(function(identity) {
                resolved = 'authenticated';
                expect(identity.Session).toBe(session);
                expect(identity.User.href).toBe('user');
            });

            $httpBackend.flush();
            expect(resolved).toBe('authenticated');
        }));

        it('can reject when there is no token', inject(function(authAdapter, $httpBackend) {
            var resolved = false, rejected = false;

            $httpBackend
                .expectPOST(TOKEN_URL).respond(500);

            authAdapter.authenticate(username, password)
                .then(function() {
                    resolved = true;
                }, function() {
                    rejected = true;
                });

            $httpBackend.flush();

            expect(resolved).toBe(false);
            expect(rejected).toBe(true);
        }));

        it('can reject on failed auth', inject(function(authAdapter, $httpBackend) {
            var resolved = false, rejected = false;

            $httpBackend.expectPOST(TOKEN_URL).respond({Token: 'token'});
            $httpBackend.expectPOST(LOGIN_URL).respond(400);

            authAdapter.authenticate(username, password)
                .then(function() {
                    resolved = true;
                }, function() {
                    rejected = true;
                });

            $httpBackend.flush();

            expect(resolved).toBe(false);
            expect(rejected).toBe(true);
        }));

    });
});
