define(['./pagination-directive'], function(paginationDirective) {
    'use strict';

    describe('pagination', function() {
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

        it('can do the math', inject(function($rootScope, $injector) {
            var scope = $rootScope.$new(true),
                TOTAL = 34,
                LIMIT = 25;

            scope.total = TOTAL;
            scope.limit = LIMIT;

            var directive = $injector.invoke(paginationDirective);
            directive.link(scope);
            $rootScope.$digest();

            expect(scope.total).toBe(TOTAL);
            expect(scope.page).toBe(0);
            expect(scope.lastPage).toBe(1);
            expect(scope.from).toBe(1);
            expect(scope.to).toBe(LIMIT);

            scope.setPage(1);
            $rootScope.$digest();

            expect(scope.page).toBe(1);
            expect(scope.lastPage).toBe(1);
            expect(scope.from).toBe(26);
            expect(scope.to).toBe(TOTAL);
        }));

    });
});
