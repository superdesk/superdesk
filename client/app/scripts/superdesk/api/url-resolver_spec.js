define(['./url-resolver-service'], function(URLResolver) {
    'use strict';

    describe('url resolver', function() {

        var SERVER_URL = 'http://localhost:5000/api',
            USERS_URL = '/users',
            RESOURCES = {_links: {child: [{title: 'users', href: USERS_URL}]}};

        beforeEach(module(function($provide) {
            $provide.service('urls', URLResolver);
            $provide.constant('config', {server: {url: SERVER_URL}});
        }));

        it('can resolve resource urls', inject(function(urls, $httpBackend, $rootScope) {
            $httpBackend.expectGET(SERVER_URL).respond(RESOURCES);

            var url;
            urls.resource('users').then(function(_url) {
                url = _url;
            });

            $httpBackend.flush();
            $rootScope.$digest();

            expect(url).toBe(SERVER_URL + USERS_URL);
        }));

        it('can resolve item urls', inject(function(urls) {
            expect(urls.item('/users/1')).toBe(SERVER_URL + '/users/1');
        }));
    });
});
