define(['lodash', 'superdesk/hashlib', 'superdesk-users/users-service'], function(_, hashlib, UsersService) {
    'use strict';

    describe('users api', function() {
        beforeEach(module(function($provide) {
            $provide.service('users', UsersService);
            $provide.service('resource', function($q) {
                this.save = function(user) {
                    if (user.Password) {
                        expect(user.Password).toBe(hashlib.hash('bar'));
                    }

                    return $q.when(_.extend({Id: 1, FullName: 'Foo Bar'}, user));
                };

                this.replace = function(dest, data) {
                    return $q.when({});
                };
            });
        }));

        it('can create user', inject(function(users, $rootScope) {

            var user = {},
                data = {'UserName': 'foo', 'Password': 'bar'};

            users.save(user, data);

            $rootScope.$digest();

            expect(user.Id).toBe(1);
            expect(data.Id).toBe(1);
            expect(user.password).toBe(undefined);
            expect(data.password).toBe(undefined);
        }));

        it('can update user', inject(function(users, $rootScope) {

            var user = {UserName: 'foo', FirstName: 'a'},
                data = {UserName: 'foo', FirstName: 'foo', LastName: 'bar'};

            users.save(user, data);

            $rootScope.$digest();

            expect(user.FirstName).toBe('foo');
            expect(data.FirstName).toBe('foo');
            expect(user.FullName).toBe('Foo Bar');
            expect(data.FullName).toBe('Foo Bar');
        }));

        it('can change user password', inject(function(users, resource, $rootScope) {

            var user = {UserPassword: {href: 'pwd_url'}};

            spyOn(resource, 'replace');

            users.changePassword(user, 'old', 'new');

            expect(resource.replace).toHaveBeenCalledWith('pwd_url', {
                OldPassword: hashlib.hash('old'),
                NewPassword: hashlib.hash('new')
            });
        }));
    });
});
