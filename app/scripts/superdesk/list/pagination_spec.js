define([
    'angular',
    './pagination-directive'
], function(angular, paginationDirective) {
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

        it('can calculate multiple pages', inject(function($rootScope, $injector, $location) {
            var scope = $rootScope.$new(true),
                ITEMS = {
                    _links: {
                        last: {
                            href: 'superdesk-api.herokuapp.com/ingest?page=2'
                        }
                    },
                    _items: [{_id: 5}, {_id: 6}]
                },
                LIMIT = 2;

            scope.items = ITEMS;
            scope.limit = LIMIT;

            $location.search('page', 1);

            var directive = $injector.invoke(paginationDirective);
            directive.link(scope);
            $rootScope.$digest();

            expect(scope.items).toBe(ITEMS);
            expect(scope.page).toBe(1);
            expect(scope.lastPage).toBe(2);
            expect(scope.from).toBe(3);
            expect(scope.to).toBe(4);
            expect(scope.approx).toBe(true);
        }));

        it('can calculate last of multiple pages', inject(function($rootScope, $injector, $location) {
            var scope = $rootScope.$new(true),
                ITEMS = {
                    _links: {
                        prev: {
                            href: 'superdesk-api.herokuapp.com/ingest?page=1'
                        }
                    },
                    _items: [{_id: 35}]
                },
                LIMIT = 2;

            scope.items = ITEMS;
            scope.limit = LIMIT;

            $location.search('page', 2);

            var directive = $injector.invoke(paginationDirective);
            directive.link(scope);
            $rootScope.$digest();

            expect(scope.items).toBe(ITEMS);
            expect(scope.page).toBe(2);
            expect(scope.lastPage).toBe(2);
            expect(scope.from).toBe(5);
            expect(scope.to).toBe(5);
            expect(scope.approx).toBe(false);
        }));

        it('can calculate only page', inject(function($rootScope, $injector, $location) {
            var scope = $rootScope.$new(true),
                ITEMS = {
                    _links: {},
                    _items: [{_id: 1}]
                },
                LIMIT = 2;

            scope.items = ITEMS;
            scope.limit = LIMIT;

            $location.search('page', 0);

            var directive = $injector.invoke(paginationDirective);
            directive.link(scope);
            $rootScope.$digest();

            expect(scope.items).toBe(ITEMS);
            expect(scope.page).toBe(0);
            expect(scope.lastPage).toBe(0);
            expect(scope.from).toBe(1);
            expect(scope.to).toBe(1);
            expect(scope.approx).toBe(false);
        }));

    });
});
