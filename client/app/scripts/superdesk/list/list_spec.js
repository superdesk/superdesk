'use strict';

describe('superdesk.list module', function() {
    beforeEach(module('templates'));
    beforeEach(module('superdesk.list'));

    describe('pagination', function() {

        var TEMPLATE = '<div sd-pagination items="items"></div>';

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
            $scope.items = {_meta: {total: 23}};
            $scope.limit = 25;

            var elem = $compile(TEMPLATE)($scope);
            $scope.$apply();

            var scope = elem.isolateScope();
            expect(scope.page).toBe(1);
            expect(scope.limit).toBe(25);
            expect(scope.lastPage).toBe(1);
            expect(scope.from).toBe(1);
            expect(scope.to).toBe(23);
        }));

        it('can calculate last of multiple pages', inject(function($compile, $rootScope, $location) {
            var $scope = $rootScope.$new(true);
            $scope.items = {_meta: {total: 26}};
            $scope.limit = 25;
            $location.search('page', 2);

            var elem = $compile(TEMPLATE)($scope);
            $scope.$apply();

            var scope = elem.isolateScope();
            expect(scope.page).toBe(2);
            expect(scope.lastPage).toBe(2);
            expect(scope.from).toBe(26);
            expect(scope.to).toBe(26);
        }));

        it('can do the math when max_results defined', inject(function($compile, $rootScope, $location) {
            var $scope = $rootScope.$new();
            $scope.items = {_meta: {total: 48}};
            $scope.limit = 25;
            $location.search('max_results', 50);

            var elem = $compile(TEMPLATE)($scope);
            $scope.$apply();

            var scope = elem.isolateScope();
            expect(scope.page).toBe(1);
            expect(scope.limit).toBe(50);
            expect(scope.lastPage).toBe(1);
            expect(scope.from).toBe(1);
            expect(scope.to).toBe(48);
        }));

        it('can calculate last of multiple pages when max_results defined',
        inject(function($compile, $rootScope, $location) {
            var $scope = $rootScope.$new(true);
            $scope.items = {_meta: {total: 55}};
            $scope.limit = 25;
            $location.search('page', 2);
            $location.search('max_results', 50);

            var elem = $compile(TEMPLATE)($scope);
            $scope.$apply();

            var scope = elem.isolateScope();
            expect(scope.page).toBe(2);
            expect(scope.lastPage).toBe(2);
            expect(scope.from).toBe(51);
            expect(scope.to).toBe(55);
        }));

    });
});
