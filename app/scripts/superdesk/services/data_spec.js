define([
    './data',
    './entity',
    './server'
], function(dataService, entityService, serverService) {
    'use strict';

    describe('DataService', function() {
        beforeEach(function() {
            module(dataService.name);
            module(entityService.name);
            module(serverService.name);
        });

        beforeEach(module(function($provide) {
            $provide.value('config', {server: {url: 'http://localhost'}});
        }));

        var DataAdapter, httpBackend;

        beforeEach(inject(function($injector) {
            DataAdapter = $injector.get('DataAdapter');
            httpBackend = $injector.get('$httpBackend');
        }));

        it('cat query resource', function() {

            var data = new DataAdapter('users'),
                users = {_items: []},
                promise = data.query({max_results: 25});

            httpBackend
                .expectGET('http://localhost/users?max_results=25')
                .respond(200, users);

            promise.then(function(result) {
                expect(result).toEqual(users);
            });

            httpBackend.flush();

            expect(data._items.length).toBe(0);
        });
    });
});
