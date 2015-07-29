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

describe('mentio directive', function() {

    beforeEach(module('superdesk.users'));
    beforeEach(module('superdesk.mocks'));
    beforeEach(module('templates'));

    beforeEach(module(function($provide) {
        $provide.service('api', function($q) {
            return function(resource) {
                return {
                    query: function() {
                        return $q.when({_items: [{_id: 1, username: 'moo'},
                            {_id: 2, username: 'foo'}, {_id: 3, username: 'fast'}]});
                    }
                };
            };
        });
    }));

    it('can return sorted users', inject(function($rootScope, $compile) {
        var scope = $rootScope.$new(true);
        var elem = $compile('<div sd-user-mentio></div>')(scope);
        scope.$digest();

        var iscope = elem.scope();
        iscope.searchUsers();
        $rootScope.$digest();
        expect(iscope.users).toEqual([{_id: 3, username: 'fast'},
            {_id: 2, username: 'foo'}, {_id: 1, username: 'moo'}]);
    }));
});

describe('user edit form', function() {
    beforeEach(module('superdesk.desks'));
    beforeEach(module('superdesk.users'));
    beforeEach(module('superdesk.mocks'));
    beforeEach(module('templates'));

    beforeEach(module(function($provide) {
        $provide.service('session', function() {
            return {
                identity: {_id: 1}
            };
        });
    }));

    it('check if first_name, last_name, phone and email are readonly', inject(function($rootScope, $compile) {
        var scope = $rootScope.$new(true);

        scope.user = {
            _id: 1,
            _readonly: {'first_name': true, 'last_name': true, 'phone': true, 'email': true},
            is_active: true,
            need_activation: false
        };

        var elm = $compile('<div sd-user-edit data-user="user"></div>')(scope);
        scope.$digest();
        expect($(elm.find('input[name=first_name]')[0]).attr('readonly')).toBeDefined();
        expect($(elm.find('input[name=last_name]')[0]).attr('readonly')).toBeDefined();
        expect($(elm.find('input[name=phone]')[0]).attr('readonly')).toBeDefined();
        expect($(elm.find('input[name=email]')[0]).attr('readonly')).toBeDefined();
    }));

    it('check if first_name, last_name, phone and email are not readonly',
        inject(function($rootScope, $compile) {
        var scope = $rootScope.$new(true);

        scope.user = {
            _id: 1,
            is_active: true,
            need_activation: false
        };

        var elm = $compile('<div sd-user-edit data-user="user"></div>')(scope);
        scope.$digest();
        expect($(elm.find('input[name=first_name]')[0]).attr('readonly')).not.toBeDefined();
        expect($(elm.find('input[name=last_name]')[0]).attr('readonly')).not.toBeDefined();
        expect($(elm.find('input[name=phone]')[0]).attr('readonly')).not.toBeDefined();
        expect($(elm.find('input[name=email]')[0]).attr('readonly')).not.toBeDefined();
    }));
});
