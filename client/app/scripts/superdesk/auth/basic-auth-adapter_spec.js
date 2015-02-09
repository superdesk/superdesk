define([
    'superdesk/api/url-resolver-service',
    './basic-auth-adapter'
], function(UrlResolverService, BasicAuthAdapter) {
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
                $provide.service('urls', UrlResolverService);
            });
        });

        it('can login', inject(function(authAdapter, urls, $q, $httpBackend) {
            $httpBackend
                .expectPOST(LOGIN_URL, {username: username, password: password})
                    .respond({token: session, user: '1'});

            spyOn(urls, 'resource').and.returnValue($q.when(LOGIN_URL));

            var identity;
            authAdapter.authenticate(username, password).then(function(_identity) {
                identity = _identity;
            });

            $httpBackend.flush();

            expect(urls.resource).toHaveBeenCalledWith('auth');
            expect(identity.token).toBe('Basic ' + btoa(session + ':'));
        }));

        it('can reject on failed auth', inject(function(authAdapter, urls, $q, $httpBackend) {
            var resolved = false, rejected = false;

            spyOn(urls, 'resource').and.returnValue($q.when(LOGIN_URL));

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
