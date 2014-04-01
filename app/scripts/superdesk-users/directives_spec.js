define([
    'superdesk-users/directives'
], function() {
    'use strict';

    var template = [
        '<form name="userForm">',
        '<input type="text" name="username" sd-user-unique data-unique-field="userName" data-exclude="user" ng-model="user.userName">',
        '<input type="password" name="password" ng-model="user.password">',
        '<input type="password" name="passwordConfirm" ng-model="user.password"',
        ' sd-password-confirm ng-model="passwordConfirm" data-password="user.password">',
        '</form>'
    ].join('');

    describe('sdUserUnique Directive', function() {
        var scope;

        beforeEach(module(function($provide) {
            $provide.service('resource', function($q) {
                this.users = {
                    // make it find foo but not any other
                    query: function(criteria) {
                        if (criteria.userName === 'foo') {
                            return $q.when({
                                total: 1,
                                _items: [{Id: 9}]
                            });
                        } else {
                            return $q.when({total: 0});
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
            scope.user = {Id: 3, userName: 'test'};
            $compile(template)(scope);

            scope.$eval('userForm.username.$setViewValue("foo")');
            scope.$digest();

            expect(scope.$eval('userForm.username.$dirty')).toBe(true);
            expect(scope.$eval('userForm.username.$valid')).toBe(false);
            expect(scope.$eval('userForm.username.$error.unique')).toBe(true);
        }));

        it('succeeds on unique constraint', inject(function($compile) {
            scope.user = {Id: 6, userName: 'baz'};
            $compile(template)(scope);

            expect(scope.$eval('userForm.username.$valid')).toBe(true);

            scope.$eval('userForm.username.$setViewValue("bar")');
            scope.$digest();

            expect(scope.$eval('userForm.username.$valid')).toBe(true);
            expect(scope.$eval('userForm.username.$error.unique')).toBe(false);
            expect(scope.$eval('userForm.username.$modelValue')).toBe('bar');
        }));

        it('succeeds failing test using exclusion', inject(function($compile) {
            scope.user = {Id: 9, userName: 'foo'};
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
            expect(scope.$eval('userForm.passwordConfirm.$error.confirm')).toBe(false);
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
