define([
    './api-service'
], function(APIProvider) {
    'use strict';

    function collection(data) {
        return {_items: data};
    }

    var USERS_URL = 'http://users_url';

    var MOCK_API = {
        type: 'mock',
        service: function() {

            this.queryLog = [];

            this.getName = function() {
                return this.name;
            };

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
            url: 'mock_url',
            data: [
                {_id: 1, username: 'foo'},
                {_id: 2, username: 'bar'}
            ]
        }
    };

    var HTTP_API = {
        type: 'http',
        service: function(resource) {
            this.resource = resource;
        },
        backend: {
            rel: '/HR/User',
            headers: {'X-Filter': 'User.*'}
        }
    };

    function doConfig($provide) {
        var apiProvider = $provide.provider('api', APIProvider);
        apiProvider.api('mock', MOCK_API);
        apiProvider.api('http', HTTP_API);

        $provide.service('urlResolver', function($q) {
            this.get = function(title) {
                return $q.when(USERS_URL);
            };
        });
    }

    describe('API Provider', function() {
        beforeEach(module(doConfig));

        it('exists', inject(function(api) {
            expect(api).toBeDefined();
        }));

        it('can register apis', inject(function(api) {
            expect(api.mock).toBeDefined();
            expect(api.http).toBeDefined();
        }));

        it('can use given service', inject(function(api) {
            expect(api.mock.getName()).toBe('mock');
        }));

        it('can override backend methods', inject(function(api, $rootScope) {
            expect(api.mock.queryLog.length).toBe(0);
            api.mock.query();
            expect(api.mock.queryLog.length).toBe(1);
        }));

        it('can define new methods', inject(function(api) {
            expect(api.mock.ping()).toBe('pong');
        }));
    });

    describe('Mock API endpoint', function() {
        beforeEach(module(doConfig));

        it('can query data', inject(function(api, $rootScope) {
            var users;
            api.mock.query().then(function(_users) {
                users = _users;
            });

            $rootScope.$digest();

            expect(users.total).toBe(2);
            expect(users._items.length).toBe(2);
        }));

        it('can find item by id', inject(function(api, $rootScope) {
            var user;
            api.mock.find(2).then(function(_user) {
                user = _user;
            });

            $rootScope.$digest();

            expect(user.username).toBe('bar');
        }));

        it('can reject fail on find', inject(function(api, $rootScope) {
            var success = jasmine.createSpy('success'),
                error = jasmine.createSpy('error');

            api.mock.find(5).then(success, error);

            $rootScope.$digest();

            expect(success).not.toHaveBeenCalled();
            expect(error).toHaveBeenCalled();
        }));

        it('can save item', inject(function(api, $rootScope) {
            var user, users;

            api.mock.save({username: 'joe'}).then(function(_user) {
                user = _user;
            });

            $rootScope.$digest();

            expect(user.username).toBe('joe');
            expect(user._id).toBe(3);

            api.mock.query().then(function(_users) {
                users = _users;
            });

            $rootScope.$digest();

            expect(users.total).toBe(3);

            api.mock.save(user, {username: 'john'});

            $rootScope.$digest();

            expect(user.username).toBe('john');

            api.mock.query({username: 'john'}).then(function(_users) {
                users = _users;
            });

            $rootScope.$digest();

            expect(users.total).toBe(1);
        }));

        it('can delete item', inject(function(api, $rootScope) {

            api.mock.remove({_id: 2});

            $rootScope.$digest();

            var users;
            api.mock.query().then(function(_users) {
                users = _users;
            });

            $rootScope.$digest();

            expect(users.total).toBe(1);
        }));

        it('can get resource url', inject(function(api, $rootScope) {
            var url;
            api.mock.getUrl().then(function(_url) {
                url = _url;
            });

            $rootScope.$digest();

            expect(url).toBe(MOCK_API.backend.url);
        }));
    });

    describe('HTTP API Endpoint', function() {

        beforeEach(module(doConfig));

        beforeEach(module(function($provide) {
        }));

        afterEach(inject(function($httpBackend) {
            $httpBackend.verifyNoOutstandingExpectation();
            $httpBackend.verifyNoOutstandingRequest();
        }));

        it('can query', inject(function(api, $httpBackend, $http) {

            var headers = $http.defaults.headers.common;
            headers['X-Filter'] = 'User.*';

            $httpBackend.expectGET(USERS_URL, headers).respond(collection([{}]));

            var users;
            api.http.query().then(function(_users) {
                users = _users;
            });

            $httpBackend.flush();

            expect(users._items.length).toBe(1);
        }));

        it('rejects on query error', inject(function(api, $httpBackend) {

            $httpBackend.expectGET(USERS_URL).respond(400);

            var reject;
            api.http.query().then(null, function(reason) {
                reject = true;
            });

            $httpBackend.flush();

            expect(reject).toBe(true);
        }));

        it('can create new resource', inject(function(api, $httpBackend) {
            var userData = {username: 'test'},
                user;

            $httpBackend.expectPOST(USERS_URL, userData).respond(201, {_links: {self: {href: 'user_href'}}});

            api.http.save({username: 'test'}).then(function(_user) {
                user = _user;
            });

            $httpBackend.flush();

            expect(user._links.self.href).toBe('user_href');
        }));

        it('can create new with diff', inject(function(api, $httpBackend) {
            var user = {},
                data = {username: 'test'};

            $httpBackend.expectPOST(USERS_URL, data).respond(201, {_links: {self: {href: 'user_href'}}});

            api.http.save(user, data);

            $httpBackend.flush();

            expect(user.username).toBe('test');
        }));

        it('can update', inject(function(api, $httpBackend) {

            var userData = {_links: {self: {href: 'user_href'}}, _id: 2, username: 'test', Avatar: {href: 'test'}},
                user;

            $httpBackend.expectPATCH('http://' + userData._links.self.href, {username: 'test', Avatar: {href: 'test'}}).respond(200);

            api.http.save(userData).then(function(_user) {
                user = _user;
            });

            $httpBackend.flush();

            expect(user.username).toBe('test');
            expect(user._links.self.href).toBe('user_href');
        }));

        it('can update with diff', inject(function(api, $httpBackend) {
            var userData = {_links: {self: {href: 'user_href'}}, _id: 2, username: 'test'},
                diff = {Active: false};

            $httpBackend.expectPATCH('http://' + userData._links.self.href, diff).respond({});

            api.http.save(userData, diff);

            $httpBackend.flush();
        }));

        it('can delete', inject(function(api, $httpBackend) {

            var user = {_links: {self: {href: 'user_href'}}},
                then = jasmine.createSpy('then');

            $httpBackend.expectDELETE('http://' + user._links.self.href).respond(204);

            api.http.remove(user).then(then);

            $httpBackend.flush();

            expect(then).toHaveBeenCalled();
        }));

        it('handles delete on deleted resource as success', inject(function(api, $httpBackend) {

            var user = {_links: {self: {href: 'user_href'}}},
                then = jasmine.createSpy('then');

            $httpBackend.expectDELETE('http://' + user._links.self.href).respond(404);

            api.http.remove(user).then(then);

            $httpBackend.flush();

            expect(then).toHaveBeenCalled();
        }));

        it('rejects other delete errors as errors', inject(function(api, $httpBackend) {
            var user = {_links: {self: {href: 'user_href'}}},
                success = jasmine.createSpy('success'),
                error = jasmine.createSpy('error');

            $httpBackend.expectDELETE('http://' + user._links.self.href).respond(405);

            api.http.remove(user).then(success, error);

            $httpBackend.flush();

            expect(success).not.toHaveBeenCalled();
            expect(error).toHaveBeenCalled();
        }));

        it('can get item by url', inject(function(api, $httpBackend) {
            var user;

            $httpBackend.expectGET('http://user_url').respond({username: 'foo'});

            api.http.getByUrl('user_url').then(function(_user) {
                user = _user;
            });

            $httpBackend.flush();

            expect(user.username).toBe('foo');
        }));

        it('can get item by id', inject(function(api, $httpBackend) {
            var user;

            $httpBackend.expectGET('http://users_url/1').respond({username: 'foo'});

            api.http.getById(1).then(function(_user) {
                user = _user;
            });

            $httpBackend.flush();

            expect(user.username).toBe('foo');

        }));

        it('can replace resource on given dest', inject(function(api, $httpBackend) {

            var data = {username: 'foo'};

            $httpBackend.expectPUT('http://user_url', data).respond({});

            api.http.replace('user_url', data);

            $httpBackend.flush();
        }));

        it('rejects non success responses', inject(function(api, $httpBackend) {
            $httpBackend.expectGET('http://some_url').respond(400);

            var success = jasmine.createSpy('success'),
                error = jasmine.createSpy('error');

            api.http.getByUrl('some_url').then(success, error);

            $httpBackend.flush();

            expect(success).not.toHaveBeenCalled();
            expect(error).toHaveBeenCalled();
        }));

        it('can get resource url', inject(function(api, $rootScope) {
            var url;

            api.http.getUrl().then(function(_url) {
                url = _url;
            });

            $rootScope.$digest();

            expect(url).toBe(USERS_URL);
        }));

        it('can get resource headers', inject(function(api) {
            expect(api.http.getHeaders()['X-Filter']).toBe('User.*');
        }));
    });

});
