define(['superdesk/directives/sdPagination'], function() {
    'use strict';

    describe('pagination', function() {
        beforeEach(module('superdesk.directives'));
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

        it('can do the math', inject(function($rootScope, $compile) {
            var scope = $rootScope.$new(true),
                TOTAL = 34,
                LIMIT = 25;

            scope.items = {total: TOTAL};

            var elem = $compile('<div sd-pagination data-total="items.total" data-limit="' + LIMIT + '"></div>')(scope);
            $rootScope.$digest();

            var iscope = elem.isolateScope();

            expect(iscope.total).toBe(TOTAL);
            expect(iscope.page).toBe(0);
            expect(iscope.lastPage).toBe(1);
            expect(iscope.from).toBe(1);
            expect(iscope.to).toBe(LIMIT);

            iscope.setPage(1);
            $rootScope.$digest();

            expect(iscope.page).toBe(1);
            expect(iscope.lastPage).toBe(1);
            expect(iscope.from).toBe(26);
            expect(iscope.to).toBe(TOTAL);
        }));

    });
});
