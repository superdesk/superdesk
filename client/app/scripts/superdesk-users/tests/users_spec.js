'use strict';

describe('users api', function() {
    beforeEach(module('superdesk.users'));
    beforeEach(module('superdesk.mocks'));

    it('can create user', inject(function(usersService, api, $q, $rootScope) {

        var user = {},
            data = {'UserName': 'foo', 'Password': 'bar'};

        spyOn(api, 'save').and.returnValue($q.when({}));

        usersService.save(user, data).then(function() {});

        $rootScope.$digest();

        expect(api.save).toHaveBeenCalled();
    }));

    it('can update user', inject(function(usersService, api, $q, $rootScope) {
        var user = {UserName: 'foo', FirstName: 'a'},
            data = {FirstName: 'foo', LastName: 'bar'};

        spyOn(api, 'save').and.returnValue($q.when({}));

        usersService.save(user, data);

        $rootScope.$digest();

        expect(api.save).toHaveBeenCalled();
        expect(user.FirstName).toBe('foo');
        expect(user.LastName).toBe('bar');
    }));

    xit('can change user password', inject(function(usersService, resource, $rootScope) {

        var user = {UserPassword: {href: 'pwd_url'}};

        spyOn(resource, 'replace');

        usersService.changePassword(user, 'old', 'new');

        expect(resource.replace).toHaveBeenCalledWith('pwd_url', {
            old_pwd: 'old',
            new_pwd: 'new'
        });
    }));
});

describe('userlist service', function() {
    beforeEach(module('superdesk.users'));
    beforeEach(module('superdesk.mocks'));

    beforeEach(module(function($provide) {
        $provide.service('api', function($q) {
            return function(resource) {
                return {
                    query: function() {
                        return $q.when({_items: [{_id: 1}, {_id: 2}, {_id: 3}]});
                    },
                    getById: function() {
                        return $q.when({_id: 1});
                    }
                };
            };
        });
    }));

    it('can fetch users', inject(function(userList, $rootScope) {
        var res = null;
        userList.get()
        .then(function(result) {
            res = result;
        });
        $rootScope.$digest();
        expect(res).toEqual({_items: [{_id: 1}, {_id: 2}, {_id: 3}]});
    }));

    it('can return users from cache', inject(function(userList, $rootScope, api) {
        userList.get().then(function(result) {});
        $rootScope.$digest();

        api = jasmine.createSpy('api');
        userList.get().then(function(result) {});
        $rootScope.$digest();

        expect(api).not.toHaveBeenCalled();
    }));

    it('can fetch single user', inject(function(userList, $rootScope) {
        var res = null;
        userList.getUser(1)
        .then(function(result) {
            res = result;
        });
        $rootScope.$digest();
        expect(res).toEqual({_id: 1});
    }));

    it('can return single user from default cacher', inject(function(userList, $rootScope, api) {
        userList.get().then(function(result) {});
        $rootScope.$digest();

        api = jasmine.createSpy('api');
        userList.getUser(1).then(function(result) {});
        $rootScope.$digest();

        expect(api).not.toHaveBeenCalled();
    }));
});
