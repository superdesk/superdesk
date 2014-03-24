define(['angular', 'superdesk/data/resource-provider'], function(angular, ResourceProvider) {
    'use strict';

    function collection(data) {
        return {collection: data};
    }

    var testMod = angular.module('test.data.provider', [])
        .constant('config', {server: {url: 'server_url'}})
        .provider('resource', ResourceProvider)
        .config(function(resourceProvider) {
            resourceProvider.resource('users', {rel: '/HR/User', headers: {'X-Filter': 'User.*'}});
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

        var links = collection([{rel: '/HR/User', href: 'users_url'}]);

        beforeEach(function() {
            module(testMod.name);
        });

        afterEach(inject(function($httpBackend) {
            $httpBackend.verifyNoOutstandingExpectation();
            $httpBackend.verifyNoOutstandingRequest();
        }));

        it('can query', inject(function(resource, $httpBackend, $http) {

            var headers = $http.defaults.headers.common;
            headers['X-Filter'] = 'User.*';

            $httpBackend.expectGET('server_url').respond(links);
            $httpBackend.expectGET('users_url', headers).respond(collection([{}]));

            var users;
            resource.users.query().then(function(_users) {
                users = _users;
            });

            $httpBackend.flush();

            expect(users._items.length).toBe(1);
        }));

        it('rejects on query error', inject(function(resource, $httpBackend) {

            $httpBackend.expectGET('server_url').respond(links);
            $httpBackend.expectGET('users_url').respond(400);

            var reject;
            resource.users.query().then(null, function(reason) {
                reject = true;
            });

            $httpBackend.flush();

            expect(reject).toBe(true);
        }));

        it('can create new resource', inject(function(resource, $httpBackend) {
            var userData = {UserName: 'test'},
                user;

            $httpBackend.expectGET('server_url').respond(links);
            $httpBackend.expectPOST('users_url', userData).respond(201, {href: 'user_href'});

            resource.users.save({UserName: 'test'}).then(function(_user) {
                user = _user;
            });

            $httpBackend.flush();

            expect(user.href).toBe('user_href');
        }));

        it('can update', inject(function(resource, $httpBackend) {

            var userData = {href: 'users_url/1', Id: 2, UserName: 'test', Avatar: {href: 'test'}},
                user;

            $httpBackend.expectPATCH(userData.href, {UserName: 'test'}).respond(200);

            resource.users.save(userData).then(function(_user) {
                user = _user;
            });

            $httpBackend.flush();

            expect(user.UserName).toBe('test');
            expect(user.href).toBe('users_url/1');
        }));

        it('can update with diff', inject(function(resource, $httpBackend) {
            var userData = {href: 'users_url/1', UserName: 'test'},
                diff = {Active: false};

            $httpBackend.expectPATCH(userData.href, diff).respond({});

            resource.users.save(userData, diff);

            $httpBackend.flush();
        }));

        it('can delete', inject(function(resource, $httpBackend) {

            var user = {href: 'users_url/1'},
                then = jasmine.createSpy('then');

            $httpBackend.expectDELETE(user.href).respond(204);

            resource.users.remove(user).then(then);

            $httpBackend.flush();

            expect(then).toHaveBeenCalled();
        }));

        it('handles delete on deleted resource as success', inject(function(resource, $httpBackend) {

            var user = {href: 'users/1'},
                then = jasmine.createSpy('then');

            $httpBackend.expectDELETE(user.href).respond(404);

            resource.users.remove(user).then(then);

            $httpBackend.flush();

            expect(then).toHaveBeenCalled();
        }));

        it('rejects other delete errors as errors', inject(function(resource, $httpBackend) {
            var user = {href: 'users/1'},
                success = jasmine.createSpy('success'),
                error = jasmine.createSpy('error');

            $httpBackend.expectDELETE(user.href).respond(405);

            resource.users.remove(user).then(success, error);

            $httpBackend.flush();

            expect(success).not.toHaveBeenCalled();
            expect(error).toHaveBeenCalled();
        }));

        it('can get item by url', inject(function(resource, $httpBackend) {
            var user;

            $httpBackend.expectGET('user_url').respond({UserName: 'foo'});

            resource.users.getByUrl('user_url').then(function(_user) {
                user = _user;
            });

            $httpBackend.flush();

            expect(user.UserName).toBe('foo');
        }));

        it('can get item by id', inject(function(resource, $httpBackend) {
            var user;

            $httpBackend.expectGET('server_url').respond(links);
            $httpBackend.expectGET('users_url/1').respond({UserName: 'foo'});

            resource.users.getById(1).then(function(_user) {
                user = _user;
            });

            $httpBackend.flush();

            expect(user.UserName).toBe('foo');

        }));

        it('can replace resource on given dest', inject(function(resource, $httpBackend) {

            var data = {UserName: 'foo'};

            $httpBackend.expectPUT('user_url', data).respond({});

            resource.users.replace('user_url', data);

            $httpBackend.flush();
        }));

        it('rejects when it has no url', inject(function(resource, $httpBackend) {
            $httpBackend.expectGET('server_url').respond(404);

            var rejected = false;

            resource.users.query().then(null, function() {
                rejected = true;
            });

            $httpBackend.flush();

            expect(rejected).toBe(true);
        }));

        it('rejects non success responses', inject(function(resource, $httpBackend) {
            $httpBackend.expectGET('some_url').respond(400);

            var success = jasmine.createSpy('success'),
                error = jasmine.createSpy('error');

            resource.users.getByUrl('some_url').then(success, error);

            $httpBackend.flush();

            expect(success).not.toHaveBeenCalled();
            expect(error).toHaveBeenCalled();
        }));

        it('can caches resource links', inject(function(resource, $httpBackend, $rootScope) {
            $httpBackend.expectGET('server_url').respond(links);
            $httpBackend.expectGET('users_url').respond(collection([]));

            resource.users.query();

            $httpBackend.flush();
            $httpBackend.expectGET('users_url').respond(collection([]));

            resource.users.query();

            $rootScope.$apply();
            $httpBackend.flush();
        }));
    });
});
