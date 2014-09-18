define([
    'angular',
    'superdesk-users/directives'
], function(angular) {
    'use strict';

    var template = [
        '<form name="userForm">',
        '<input type="text" name="username" sd-user-unique data-unique-field="username" data-exclude="user" ng-model="user.username">',
        '<input type="password" name="password" ng-model="user.password">',
        '<input type="password" name="passwordConfirm" ng-model="_confirm"',
        ' sd-password-confirm ng-model="passwordConfirm" data-password="user.password">',
        '</form>'
    ].join('');

    describe('sdUserUnique Directive', function() {
        var scope;

        beforeEach(module(function($provide) {
            $provide.service('api', function($q) {
                this.users = {
                    // make it find foo but not any other
                    query: function(criteria) {
                        if (criteria.where && criteria.where.username === 'foo') {
                            return $q.when({
                                _items: [{_id: 9, username: 'foo'}]
                            });
                        } else {
                            return $q.when({_items: []});
                        }
                    }
                };
            });
        }));

        beforeEach(module('superdesk.users.directives'));

        beforeEach(inject(function($rootScope) {
            scope = $rootScope.$new(true);
        }));

        it('fails on unique constraint', inject(function($compile) {
            scope.user = {_id: 3, username: 'test'};
            $compile(template)(scope);

            scope.$eval('userForm.username.$setViewValue("foo")');
            scope.$digest();

            expect(scope.$eval('userForm.username.$dirty')).toBe(true);
            expect(scope.$eval('userForm.username.$valid')).toBe(false);
            expect(scope.$eval('userForm.username.$error.unique')).toBe(true);
        }));

        it('succeeds on unique constraint', inject(function($compile) {
            scope.user = {_id: 6, username: 'baz'};
            $compile(template)(scope);

            expect(scope.$eval('userForm.username.$valid')).toBe(true);

            scope.$eval('userForm.username.$setViewValue("bar")');
            scope.$digest();

            expect(scope.$eval('userForm.username.$valid')).toBe(true);
            expect(scope.$eval('userForm.username.$error.unique')).toBe(undefined);
            expect(scope.$eval('userForm.username.$modelValue')).toBe('bar');
        }));

        it('succeeds failing test using exclusion', inject(function($compile) {
            scope.user = {_id: 9, username: 'foo'};
            $compile(template)(scope);

            scope.$eval('userForm.username.$setViewValue("foo")');
            scope.$digest();

            expect(scope.$eval('userForm.username.$valid')).toBe(true);
        }));

        it('fails confirming password', inject(function($compile) {
            scope.user = {password: 'test'};
            $compile(template)(scope);

            scope.$eval('userForm.passwordConfirm.$setViewValue("not-test")');
            scope.$digest();

            expect(scope.$eval('userForm.passwordConfirm.$dirty')).toBe(true);
            expect(scope.$eval('userForm.passwordConfirm.$valid')).toBe(false);
            expect(scope.$eval('userForm.passwordConfirm.$error.confirm')).toBe(true);
        }));

        it('succeeds confirming password', inject(function($compile) {
            scope.user = {password: 'test'};
            $compile(template)(scope);

            scope.$eval('userForm.passwordConfirm.$setViewValue("test")');
            scope.$digest();

            expect(scope.$eval('userForm.passwordConfirm.$valid')).toBe(true);
            expect(scope.$eval('userForm.passwordConfirm.$error.confirm')).toBe(undefined);
        }));

    });

    describe('user edit directive', function() {
        function noop() {
        }

        beforeEach(module(function($provide) {
            $provide.service('gettext', noop);
            $provide.service('api', noop);
            $provide.service('notify', noop);
            $provide.service('resource', noop);
            $provide.service('$route', noop);
            $provide.service('superdesk', noop);
            $provide.provider('translateFilter', function() {
                this.$get = function() {
                    return angular.identity;
                };
            });
        }));

        beforeEach(module('superdesk.users.directives'));
        beforeEach(module('templates'));

        it('checks username for valid characters', inject(function($compile, $rootScope) {
            var scope = $rootScope.$new(true),
                elem = $compile('<div sd-user-edit></div>')(scope);

            scope.$digest();
            var dirScope = elem.isolateScope();

            expect(dirScope.usernamePattern.test('!')).toBe(false);
            expect(dirScope.usernamePattern.test('@')).toBe(false);
            expect(dirScope.usernamePattern.test('#')).toBe(false);
            expect(dirScope.usernamePattern.test(' ')).toBe(false);

            expect(dirScope.usernamePattern.test('.')).toBe(true);
            expect(dirScope.usernamePattern.test('_')).toBe(true);
            expect(dirScope.usernamePattern.test('-')).toBe(true);
            expect(dirScope.usernamePattern.test('\'')).toBe(true);

            expect(dirScope.usernamePattern.test('b')).toBe(true);
            expect(dirScope.usernamePattern.test('B')).toBe(true);
            expect(dirScope.usernamePattern.test('1')).toBe(true);
        }));

        it('checks phone number for valid characters', inject(function($compile, $rootScope) {
            var scope = $rootScope.$new(true),
                elem = $compile('<div sd-user-edit></div>')(scope);

            scope.$digest();
            var dirScope = elem.isolateScope();

            expect(dirScope.phonePattern.test('z')).toBe(false);
            expect(dirScope.phonePattern.test('zxcvbnmas')).toBe(false);

            expect(dirScope.phonePattern.test('12345678')).toBe(false);
            expect(dirScope.phonePattern.test('123456789')).toBe(true);
            expect(dirScope.phonePattern.test('+1234567890')).toBe(true);
            expect(dirScope.phonePattern.test('+123456789000')).toBe(true);

            expect(dirScope.phonePattern.test('+')).toBe(false);
            expect(dirScope.phonePattern.test('$')).toBe(false);
            expect(dirScope.phonePattern.test('$$$$$$$$$')).toBe(false);
        }));

    });
});
