define(['./url-resolver-service'], function(URLResolver) {
    'use strict';

    describe('url resolver', function() {

        var SERVER_URL = 'http://localhost',
            USERS_URL = '/users',
            RESOURCES = {_links: {child: [{title: 'users', href: USERS_URL}]}};

        beforeEach(module(function($provide) {
            $provide.service('urls', URLResolver);
            $provide.constant('config', {server: {url: SERVER_URL}});
        }));

        it('can resolve urls by title', inject(function(urls, $httpBackend, $rootScope) {
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
            expect(urls.item('/item')).toBe(SERVER_URL + '/item');
        }));
    });

    describe('url resolver when server has prefix', function() {

        var SERVER_URL = 'http://localhost:5000/api';

        beforeEach(module(function($provide) {
            $provide.service('urls', URLResolver);
            $provide.constant('config', {server: {url: SERVER_URL}});
        }));

        it('can handle server url prefix', inject(function(urls, $httpBackend) {

            $httpBackend.expectGET(SERVER_URL).respond({
                _links: {
                    child: [
                        {title: 'users', href: '/api/users'}
                    ]
                }
            });

            var url;
            urls.resource('users').then(function(_url) {
                url = _url;
            });

            $httpBackend.flush();

            expect(url).toBe('http://localhost:5000/api/users');

        }));
    });
});
