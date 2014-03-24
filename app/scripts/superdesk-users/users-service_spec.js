define(['lodash', 'superdesk/hashlib', 'superdesk-users/users-service'], function(_, hashlib, UsersService) {
    'use strict';

    describe('users api', function() {

        beforeEach(module(function($provide) {
            $provide.service('api', UsersService);
            $provide.service('resource', function($q) {
                this.users = {
                    save: function(user) {
                        if (user.Password) {
                            expect(user.Password).toBe(hashlib.hash('bar'));
                        }

                        return $q.when(_.extend({Id: 1, FullName: 'Foo Bar'}, user));
                    },
                    replace: function(dest, data) {
                        return $q.when({});
                    }
                };
            });
        }));

        it('exists', inject(function(api) {
            expect(api.users).not.toBe(undefined);
        }));

        it('can create user', inject(function(api, $rootScope) {

            var user = {},
                data = {'UserName': 'foo', 'Password': 'bar'};

            api.users.save(user, data);

            $rootScope.$digest();

            expect(user.Id).toBe(1);
            expect(data.Id).toBe(1);
            expect(user.password).toBe(undefined);
            expect(data.password).toBe(undefined);
        }));

        it('can update user', inject(function(api, $rootScope) {

            var user = {UserName: 'foo', FirstName: 'a'},
                data = {UserName: 'foo', FirstName: 'foo', LastName: 'bar'};

            api.users.save(user, data);

            $rootScope.$digest();

            expect(user.FirstName).toBe('foo');
            expect(data.FirstName).toBe('foo');
            expect(user.FullName).toBe('Foo Bar');
            expect(data.FullName).toBe('Foo Bar');
        }));

        it('can change user password', inject(function(api, resource, $rootScope) {

            var user = {UserPassword: {href: 'pwd_url'}};

            spyOn(resource.users, 'replace');

            api.users.changePassword(user, 'old', 'new');

            expect(resource.users.replace).toHaveBeenCalledWith('pwd_url', {
                OldPassword: hashlib.hash('old'),
                NewPassword: hashlib.hash('new')
            });
        }));
    });
});
