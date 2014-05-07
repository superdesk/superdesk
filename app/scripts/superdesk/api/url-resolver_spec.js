define(['./url-resolver-service'], function(URLResolver) {
    'use strict';

    describe('url resolver', function() {

        var SERVER_URL = 'server_url',
            USERS_URL = 'localhost/users',
            RESOURCES = {_links: {child: [{title: 'users', href: USERS_URL}]}};

        beforeEach(module(function($provide) {
            $provide.service('urls', URLResolver);
            $provide.constant('config', {server: {url: SERVER_URL}});
        }));

        it('can resolve urls by title', inject(function(urls, $httpBackend, $rootScope) {
            $httpBackend.expectGET(SERVER_URL).respond(RESOURCES);

            var url;
            urls.get('users').then(function(_url) {
                url = _url;
            });

            $httpBackend.flush();
            $rootScope.$digest();

            expect(url).toBe('http://' + USERS_URL);
        }));
    });
});
