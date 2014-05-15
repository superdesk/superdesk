define([
    './api-service',
    './url-resolver-service'
], function(APIProvider, UrlResolver) {
    'use strict';

    function collection(data) {
        return {_items: data};
    }

    var USERS_URL = 'http://users_url',
        SERVER_URL = 'http://localhost';

    var HTTP_API = {
        type: 'http',
        service: function() {
            this.queryLog = [];

            var query = this.query;
            this.query = function(criteria) {
                this.queryLog.push(criteria);
                return query.call(this, criteria);
            };

            this.ping = function() {
                return 'pong';
            };
        },
        backend: {
            rel: 'users',
            headers: {'X-Filter': 'User.*'}
        }
    };

    function doConfig($provide) {
        $provide.service('urls', UrlResolver);
        $provide.constant('config', {server: {url: SERVER_URL}});
        var apiProvider = $provide.provider('api', APIProvider);
        apiProvider.api('http', HTTP_API);
    }

    describe('API Provider', function() {
        beforeEach(module(doConfig));

        it('exists', inject(function(api) {
            expect(api).toBeDefined();
        }));

        it('can register apis', inject(function(api) {
            expect(api.http).toBeDefined();
        }));

        it('can override backend methods', inject(function(api, $rootScope) {
            expect(api.http.queryLog.length).toBe(0);
            api.http.query();
            expect(api.http.queryLog.length).toBe(1);
        }));

        it('can define new methods', inject(function(api) {
            expect(api.http.ping()).toBe('pong');
        }));
    });

    describe('HTTP API Endpoint', function() {

        beforeEach(module(doConfig));

        afterEach(inject(function($httpBackend) {
            $httpBackend.verifyNoOutstandingExpectation();
            $httpBackend.verifyNoOutstandingRequest();
        }));

        it('can query', inject(function(api, urls, $q, $httpBackend, $http) {

            var headers = $http.defaults.headers.common;
            headers['X-Filter'] = 'User.*';

            spyOn(urls, 'resource').andReturn($q.when(USERS_URL));

            $httpBackend.expectGET(USERS_URL, headers).respond(collection([{}]));

            var users;
            api.http.query().then(function(_users) {
                users = _users;
            });

            $httpBackend.flush();

            expect(users._items.length).toBe(1);
            expect(urls.resource).toHaveBeenCalledWith('users');
        }));

        it('rejects on query error', inject(function(api, urls, $q, $httpBackend) {

            $httpBackend.expectGET(USERS_URL).respond(400);

            spyOn(urls, 'resource').andReturn($q.when(USERS_URL));

            var reject;
            api.http.query().then(null, function(reason) {
                reject = true;
            });

            $httpBackend.flush();

            expect(reject).toBe(true);
        }));

        it('can create new resource', inject(function(api, urls, $q, $httpBackend) {
            var userData = {username: 'test'},
                user;

            spyOn(urls, 'resource').andReturn($q.when(USERS_URL));

            $httpBackend.expectPOST(USERS_URL, userData).respond(201, {_links: {self: {href: 'user_href'}}});

            api.http.save({username: 'test'}).then(function(_user) {
                user = _user;
            });

            $httpBackend.flush();

            expect(user._links.self.href).toBe('user_href');
            expect(urls.resource).toHaveBeenCalledWith('users');
        }));

        it('can fail creating new resource', inject(function(api, urls, $q, $httpBackend) {
            var userData = {username: 'test'};

            spyOn(urls, 'resource').andReturn($q.when(USERS_URL));

            $httpBackend.expectPOST(USERS_URL, userData).respond(200, {
                _status: 'ERR',
                _issues: {first_name: {required: 1}}
            });

            var test = null;

            api.http.save({username: 'test'}).then(function(response) {
                test = true;
            }, function(response) {
                test = false;
            });

            $httpBackend.flush();

            expect(test).toBe(false);
        }));

        it('can create new with diff', inject(function(api, urls, $q, $httpBackend) {
            var user = {},
                data = {username: 'test'};

            spyOn(urls, 'resource').andReturn($q.when(USERS_URL));

            $httpBackend.expectPOST(USERS_URL, data).respond(201, {_links: {self: {href: 'user_href'}}});

            api.http.save(user, data);

            $httpBackend.flush();

            expect(user.username).toBe('test');
            expect(urls.resource).toHaveBeenCalledWith('users');
        }));

        it('can update', inject(function(api, $httpBackend) {

            var userData = {_links: {self: {href: '/user_href'}}, _id: 2, username: 'test', Avatar: {href: 'test'}},
                user;

            $httpBackend.expectPATCH(SERVER_URL + userData._links.self.href, {username: 'test', Avatar: {href: 'test'}}).respond(200);

            api.http.save(userData).then(function(_user) {
                user = _user;
            });

            $httpBackend.flush();

            expect(user.username).toBe('test');
            expect(user._links.self.href).toBe('/user_href');
        }));

        it('can update with diff', inject(function(api, $httpBackend) {
            var userData = {_links: {self: {href: '/user_href'}}, _id: 2, username: 'test'},
                diff = {Active: false};

            $httpBackend.expectPATCH(SERVER_URL + userData._links.self.href, diff).respond({});

            api.http.save(userData, diff);

            $httpBackend.flush();
        }));

        it('can delete', inject(function(api, $httpBackend) {

            var user = {_links: {self: {href: '/user_href'}}},
                then = jasmine.createSpy('then');

            $httpBackend.expectDELETE(SERVER_URL + user._links.self.href).respond(204);

            api.http.remove(user).then(then);

            $httpBackend.flush();

            expect(then).toHaveBeenCalled();
        }));

        it('handles delete on deleted resource as success', inject(function(api, $httpBackend) {

            var user = {_links: {self: {href: '/user_href'}}},
                then = jasmine.createSpy('then');

            $httpBackend.expectDELETE(SERVER_URL + user._links.self.href).respond(404);

            api.http.remove(user).then(then);

            $httpBackend.flush();

            expect(then).toHaveBeenCalled();
        }));

        it('rejects other delete errors as errors', inject(function(api, $httpBackend) {
            var user = {_links: {self: {href: '/user_href'}}},
                success = jasmine.createSpy('success'),
                error = jasmine.createSpy('error');

            $httpBackend.expectDELETE(SERVER_URL + user._links.self.href).respond(405);

            api.http.remove(user).then(success, error);

            $httpBackend.flush();

            expect(success).not.toHaveBeenCalled();
            expect(error).toHaveBeenCalled();
        }));

        it('can get item by url', inject(function(api, $httpBackend) {
            var user;

            $httpBackend.expectGET(SERVER_URL + '/user_url').respond({username: 'foo'});

            api.http.getByUrl('/user_url').then(function(_user) {
                user = _user;
            });

            $httpBackend.flush();

            expect(user.username).toBe('foo');
        }));

        it('can get item by id', inject(function(api, urls, $q, $httpBackend) {
            var user;

            spyOn(urls, 'resource').andReturn($q.when(SERVER_URL + '/users'));

            $httpBackend.expectGET(SERVER_URL + '/users/1').respond({username: 'foo'});

            api.http.getById(1).then(function(_user) {
                user = _user;
            });

            $httpBackend.flush();

            expect(user.username).toBe('foo');
            expect(urls.resource).toHaveBeenCalledWith('users');

        }));

        it('can replace resource on given dest', inject(function(api, $httpBackend) {

            var data = {username: 'foo'};

            $httpBackend.expectPUT(SERVER_URL + '/user_url', data).respond({});

            api.http.replace('/user_url', data);

            $httpBackend.flush();
        }));

        it('rejects non success responses', inject(function(api, $httpBackend) {
            $httpBackend.expectGET(SERVER_URL + '/some_url').respond(400);

            var success = jasmine.createSpy('success'),
                error = jasmine.createSpy('error');

            api.http.getByUrl('/some_url').then(success, error);

            $httpBackend.flush();

            expect(success).not.toHaveBeenCalled();
            expect(error).toHaveBeenCalled();
        }));

        it('can get resource url', inject(function(api, urls, $q, $rootScope) {
            var url;

            spyOn(urls, 'resource').andReturn($q.when(USERS_URL));

            api.http.getUrl().then(function(_url) {
                url = _url;
            });

            $rootScope.$digest();

            expect(url).toBe(USERS_URL);
            expect(urls.resource).toHaveBeenCalledWith('users');
        }));

        it('can get resource headers', inject(function(api) {
            expect(api.http.getHeaders()['X-Filter']).toBe('User.*');
        }));
    });

});
