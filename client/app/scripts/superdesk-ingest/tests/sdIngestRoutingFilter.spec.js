
/**
* Module with tests for the sdIngestRoutingFilter directive
*
* @module sdIngestRoutingFilter directive tests
*/
describe('sdIngestRoutingFilter directive', function () {
    'use strict';

    var scope,  // the directive's own isolate scope
        $compile,
        $rootScope;

    beforeEach(module('superdesk.templates-cache'));
    beforeEach(module('superdesk.ingest'));

    beforeEach(inject(function (_$compile_, _$rootScope_) {
        $compile = _$compile_;
        $rootScope = _$rootScope_;
    }));

    /**
     * Compiles the directive under test and links it with a new scope
     * containing the provided scope values.
     *
     * @function compileDirective
     * @param {Object} scopeValues - values in the current scope of the DOM
     *   element the directive will be applied to
     * @return {Object} - the root DOM node of the compiled directive element
     */
    function compileDirective(scopeValues) {
        var html,
            parentScope,  // scope of the element the directive is applied to
            $element;

        parentScope = $rootScope.$new();
        angular.extend(parentScope, scopeValues);

        html = [
            '<div sd-ingest-routing-filter ',
            '    rule="rule" content-filters="contentFilters"',
            '></div>'
        ].join('');

        $element = $compile(html)(parentScope);
        parentScope.$digest();

        return $element;
    }

    beforeEach(inject(function () {
        var parentScopeValues = {rule: {filter: 'foobar'}},
            $element;

        $element = compileDirective(parentScopeValues);
        scope = $element.isolateScope();
    }));

    describe('on scope initialization', function () {
        it('makes the list of matching filters empty', function () {
            expect(scope.matchingFilters).toEqual([]);
        });

        it('clears the current content filter search term', function () {
            expect(scope.filterSearchTerm).toBe(null);
        });

        it('sets the selected content filter if it exists', function () {
            var parentScopeValues,
                $element;

            parentScopeValues = {
                rule: {filter: 'bar'},
                contentFilters: [{_id: 'foo'}, {_id: 'bar'}, {_id: 'baz'}]
            };

            $element = compileDirective(parentScopeValues);
            scope = $element.isolateScope();

            expect(scope.selectedFilter).toEqual({_id: 'bar'});
        });

        it('sets the selected content to null if it does not exist',
            function () {
                var parentScopeValues,
                    $element;

                parentScopeValues = {
                    rule: {filter: null},
                    contentFilters: [{_id: 'foo'}, {_id: 'bar'}, {_id: 'baz'}]
                };

                $element = compileDirective(parentScopeValues);
                scope = $element.isolateScope();

                expect(scope.selectedFilter).toBe(null);
            }
        );
    });

    describe('searchFilters() scope method', function () {
        it('changes the matching filters list to only contain those content ' +
            'filters that match the search term',
            function () {
                var expectedIds,
                    matchIds;

                scope.filters = [
                    {id: 1, name: 'foo-bar name'},
                    {id: 2, name: 'body contains "Foo+1" phrase'},
                    {id: 3, name: 'text items named Foo*'},
                    {id: 4, name: 'foooo1 in slugline'},
                    {id: 5, name: 'breaking foo+1 news stories'}
                ];

                scope.matchingFilters = [];
                scope.searchFilters('foo+1');

                matchIds = _.pluck(scope.matchingFilters, 'id').sort();
                expectedIds = [2, 5].sort();
                expect(matchIds).toEqual(expectedIds);
            }
        );
    });

    describe('selectFilter() scope method', function () {
        var contentFilter;

        beforeEach(function () {
            contentFilter = {_id: 'abcd123', name: 'My Filter'};
            scope.rule = {};
        });

        it('sets the selected filter in scope to the given filter',
            function () {
                scope.selectedFilter = null;
                scope.selectFilter(contentFilter);
                expect(scope.selectedFilter).toEqual(contentFilter);
            }
        );

        it('sets the routing rule\'s filter to the given filter', function () {
            scope.rule.filter = null;
            scope.selectFilter(contentFilter);
            expect(scope.rule.filter).toEqual('abcd123');
        });

        it('sets the routing rule\'s filter name to the given filter',
            function () {
                scope.rule.filterName = null;
                scope.selectFilter(contentFilter);
                expect(scope.rule.filterName).toEqual('My Filter');
            }
        );

        it('clears the filter search term', function () {
            scope.filterSearchTerm = 'foo';
            scope.selectFilter(contentFilter);
            expect(scope.filterSearchTerm).toBe(null);
        });
    });

    describe('clearSelectedFilter() scope method', function () {
        beforeEach(function () {
            scope.rule = {};
        });

        it('clears the selected filter in scope', function () {
            scope.selectedFilter = {};
            scope.clearSelectedFilter();
            expect(scope.selectedFilter).toBe(null);
        });

        it('clears the routing rule\'s filter', function () {
            scope.rule.filter = 'f1lt3rId';
            scope.clearSelectedFilter();
            expect(scope.rule.filter).toBe(null);
        });

        it('sets the routing rule\'s filter name', function () {
            scope.rule.filterName = 'Some Filter';
            scope.clearSelectedFilter();
            expect(scope.rule.filterName).toBe(null);
        });
    });
});
