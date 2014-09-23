define(['superdesk-users/userlist-service'], function(UserListService) {
    'use strict';

    describe('userlist service', function() {
        beforeEach(module(function($provide) {
            $provide.service('userList', UserListService);
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
});
