define([
    'angular',
    './list'
], function(angular) {
    'use strict';

    describe('superdesk.list module', function() {
        beforeEach(module('templates'));
        beforeEach(module('superdesk.list'));

        describe('pagination', function() {

            var TEMPLATE = '<div sd-pagination items="items" limit="limit"></div>';

            beforeEach(module('templates'));
            beforeEach(module(function($provide) {
                $provide.provider('translateFilter', function() {
                    this.$get = function() {
                        return function(text) {
                            return text;
                        };
                    };
                });
            }));

            it('can do the math', inject(function($compile, $rootScope) {
                var $scope = $rootScope.$new();
                $scope.items = {_meta: {total: 3}};
                $scope.limit = 5;

                var elem = $compile(TEMPLATE)($scope);
                $scope.$apply();

                var scope = elem.isolateScope();
                expect(scope.page).toBe(1);
                expect(scope.limit).toBe(5);
                expect(scope.lastPage).toBe(1);
                expect(scope.from).toBe(1);
                expect(scope.to).toBe(3);
            }));

            it('can calculate last of multiple pages', inject(function($compile, $rootScope, $location) {
                var $scope = $rootScope.$new(true);
                $scope.items = {_meta: {total: 3}};
                $scope.limit = 2;
                $location.search('page', 2);

                var elem = $compile(TEMPLATE)($scope);
                $scope.$apply();

                var scope = elem.isolateScope();
                expect(scope.page).toBe(2);
                expect(scope.lastPage).toBe(2);
                expect(scope.from).toBe(3);
                expect(scope.to).toBe(3);
            }));
        });
    });
});
