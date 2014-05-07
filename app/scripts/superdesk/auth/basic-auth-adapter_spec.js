define([
    './basic-auth-adapter'
], function(BasicAuthAdapter) {
    'use strict';

    /* jshint maxlen:false */
    var SERVER_URL = 'http://localhost/resource',
        LOGIN_URL = SERVER_URL + '/auth',
        username = 'admin',
        password = 'admin',
        session = 'xyz';

    describe('basic auth adapter', function() {
        beforeEach(function() {
            module(function($provide) {
                $provide.constant('config', {server: {url: SERVER_URL}});
                $provide.service('authAdapter', BasicAuthAdapter);
            });
        });

        it('can login', inject(function(authAdapter, $httpBackend) {
            $httpBackend
                .expectPOST(LOGIN_URL, {username: username, password: password})
                    .respond({token: session, user: '1'});

            var identity;
            authAdapter.authenticate(username, password).then(function(_identity) {
                identity = _identity;
            });

            $httpBackend.flush();

            expect(identity.token).toBe(session);
        }));

        it('can reject on failed auth', inject(function(authAdapter, $httpBackend) {
            var resolved = false, rejected = false;

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
