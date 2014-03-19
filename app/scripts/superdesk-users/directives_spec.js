define([
    'superdesk-users/directives'
], function() {
    'use strict';

    var template = [
        '<form name="userForm">',
        '<input type="text" name="username" sd-user-unique data-unique-field="userName" ng-model="userName">',
        '</form>'
    ].join('');

    describe('sdUserUnique Directive', function() {

        beforeEach(module(function($provide) {
            $provide.service('resource', function($q) {
                this.users = {
                    // make it find foo but not any other
                    query: function(criteria) {
                        return $q.when({total: criteria.userName === 'foo' ? 1 : 0});
                    }
                };
            });
        }));

        beforeEach(module('superdesk.users.directives'));

        it('validates that field is unique', inject(function($rootScope, $compile) {
            var scope = $rootScope.$new(true);

            $compile(template)(scope);

            scope.$eval('userForm.username.$setViewValue("foo")');
            scope.$digest();

            expect(scope.$eval('userForm.username.$dirty')).toBe(true);
            expect(scope.$eval('userForm.username.$valid')).toBe(false);
            expect(scope.$eval('userForm.username.$error.unique')).toBe(true);

            scope.$eval('userForm.username.$setViewValue("bar")');
            scope.$digest();

            expect(scope.$eval('userForm.username.$valid')).toBe(true);
            expect(scope.$eval('userForm.username.$error.unique')).toBe(false);
        }));

    });
});
