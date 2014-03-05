define(['angular', 'superdesk/data/resource-provider'], function(angular, ResourceProvider) {
    'use strict';

    function collection(data) {
        return {collection: data};
    }

    var testMod = angular.module('test.data.provider', [])
        .constant('config', {server: {url: 'http://localhost'}})
        .provider('resource', ResourceProvider)
        .config(function(resourceProvider) {
            resourceProvider.resource('users', {rel: '/HR/User'});
        });

    describe('resource provider', function() {

        beforeEach(function() {
            module(testMod.name);
        });

        it('can be loaded', function() {
            expect(!!ResourceProvider).toBe(true);
        });

        it('can create service', inject(function(resource) {
            expect(!!resource).toBe(true);
        }));
    });

    describe('resource service', function() {

        var resources = collection([{rel: '/HR/User', href: 'users_url'}]);

        beforeEach(function() {
            module(testMod.name);
        });

        it('can query', inject(function(resource, $httpBackend) {

            $httpBackend.expectGET('http://localhost').respond(resources);
            $httpBackend.expectGET('users_url').respond(collection([{}]));

            var users;
            resource.users.query().then(function(_users) {
                users = _users;
            });

            $httpBackend.flush();

            expect(users._items.length).toBe(1);
        }));

        it('rejects on query error', inject(function(resource, $httpBackend) {

            $httpBackend.expectGET('http://localhost').respond(resources);
            $httpBackend.expectGET('users_url').respond(400);

            var users, reject;
            resource.users.query().then(function(_users) {
                users = _users;
            }, function(reason) {
                reject = reason;
            });

            $httpBackend.flush();

            expect(!!users).toBe(false);
            expect(!!reject).toBe(true);
        }));

        it('can create new resource', inject(function(resource, $httpBackend) {
            var userData = {UserName: 'test'},
                user;

            $httpBackend.expectGET('http://localhost').respond(resources);
            $httpBackend.expectPOST('users_url', userData).respond(201, {href: 'user_href'});

            resource.users.save({UserName: 'test'}).then(function(_user) {
                user = _user;
            });

            $httpBackend.flush();

            expect(user.href).toBe('user_href');
        }));

        it('can update', inject(function(resource, $httpBackend) {

            var userData = {href: 'users_url/1', UserName: 'test'},
                user;

            $httpBackend.expectPATCH(userData.href, {UserName: 'test'}).respond(200);

            resource.users.save(userData).then(function(_user) {
                user = _user;
            });

            $httpBackend.flush();

            expect(user.UserName).toBe('test');
            expect(user.href).toBe('users_url/1');
        }));

        it('can delete', inject(function(resource, $httpBackend) {

            var userData = {href: 'users_url/1'},
                deleted;

            $httpBackend.expectDELETE(userData.href).respond(204);

            resource.users.remove(userData).then(function(_deleted) {
                deleted = true;
            });

            $httpBackend.flush();

            expect(deleted).toBe(true);

        }));
    });
});
