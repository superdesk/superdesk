'use strict';

describe('search service', function() {
    beforeEach(module('templates'));
    beforeEach(module('superdesk.search'));

    it('can create base query', inject(function(search) {
        var query = search.query();
        var criteria = query.getCriteria();
        var filters = criteria.query.filtered.filter.and;
        expect(filters).toContain({not: {term: {state: 'spiked'}}});
        expect(filters).toContain({not: {and: [{term: {package_type: 'takes'}}, {term: {_type: 'archive'}}]}});
        expect(filters).toContain({not: {and: [{term: {_type: 'published'}},
                {term: {package_type: 'takes'}},
                {term: {last_published_version: false}}]}});
        expect(criteria.sort).toEqual([{versioncreated: 'desc'}]);
        expect(criteria.size).toBe(25);
    }));

    it('can create query string query', inject(function($rootScope, search) {
        var criteria = search.query({q: 'test'}).getCriteria();
        expect(criteria.query.filtered.query.query_string.query).toBe('test');
    }));

    it('can set size', inject(function(search) {
        var criteria = search.query().size(10).getCriteria();
        expect(criteria.size).toBe(10);
    }));

    it('can sort items', inject(function(search, $location, $rootScope) {
        search.setSort('urgency');
        $rootScope.$digest();
        expect($location.search().sort).toBe('urgency:desc');
        expect(search.getSort()).toEqual({label: 'News Value', field: 'urgency', dir: 'desc'});

        search.toggleSortDir();
        $rootScope.$digest();
        expect(search.getSort()).toEqual({label: 'News Value', field: 'urgency', dir: 'asc'});
    }));

    it('can be watched for changes', inject(function(search, $rootScope) {
        var criteria = search.query().getCriteria();
        expect(criteria).toEqual(search.query().getCriteria());
        expect(criteria).not.toEqual(search.query({q: 'test'}).getCriteria());
    }));

    describe('multi action bar directive', function() {

        var scope;

        beforeEach(module('superdesk.archive'));
        beforeEach(module('superdesk.packaging'));
        beforeEach(module('superdesk.authoring.multiedit'));

        beforeEach(inject(function($rootScope, $compile) {
            var elem = $compile('<div sd-multi-action-bar></div>')($rootScope.$new());
            scope = elem.scope();
            scope.$digest();
        }));

        it('can show how many items are selected', inject(function() {
            expect(scope.multi.count).toBe(0);

            scope.multi.toggle({_id: 1, selected: true});
            expect(scope.multi.count).toBe(1);

            scope.multi.reset();
            expect(scope.multi.count).toBe(0);
        }));

        it('can trigger multi editing', inject(function(multiEdit) {
            spyOn(multiEdit, 'create');
            spyOn(multiEdit, 'open');

            scope.multi.toggle({_id: 'foo', selected: true});
            scope.multi.toggle({_id: 'bar', selected: true});

            scope.action.multiedit();
            expect(multiEdit.create).toHaveBeenCalledWith(['foo', 'bar']);
            expect(multiEdit.open).toHaveBeenCalled();
        }));
    });
});

describe('sdSearchFacets directive', function () {
    var desks,
        facetsInit,
        fakeApi,
        fakeMetadata,
        isoScope,
        $element;  // directive's DOM element

    beforeEach(module(
        'superdesk.authoring.metadata',
        'superdesk.search',
        'templates'  // needed so that directive's template is placed into
                     // $templateCache, avoiding the "Unexpected request" error
    ));

    /**
     * Mock some of the dependencies of the parent directives.
     */
    beforeEach(module(function ($provide) {
        fakeApi = {
            ingestProviders: {
                query: jasmine.createSpy()
            }
        };

        fakeMetadata = {
            values: {subjectcodes: []},
            fetchSubjectcodes: jasmine.createSpy()
        };

        $provide.value('api', fakeApi);
        $provide.value('metadata', fakeMetadata);
    }));

    /**
     * Mock even more dependencies and compile the directive under test.
     */
    beforeEach(inject(function (
        $templateCache, $compile, $rootScope, $q, _desks_, tags, search
    ) {
        var html,
            scope;

        // more services mocking...
        spyOn(search, 'getSubjectCodes').and.returnValue([]);

        desks = _desks_;
        spyOn(desks, 'initialize');

        facetsInit = $q.defer();
        spyOn(tags, 'initSelectedFacets').and.returnValue(facetsInit.promise);

        fakeApi.ingestProviders.query.and.returnValue(
            $q.when({_items: [{foo: 'bar'}]})
        );
        fakeMetadata.fetchSubjectcodes.and.returnValue($q.when());

        // directive compilation...
        html = [
            '<div sd-search-container>',
            '    <div sd-search-facets></div>',
            '</div>'
        ].join('');

        scope = $rootScope.$new();

        $element = $compile(html)(scope).find('div[sd-search-facets]');
        scope.$digest();

        isoScope = $element.isolateScope();
    }));

    describe('reacting to changes in the item list', function () {
        beforeEach(function () {
            isoScope.items = {
                _aggregations: {
                    desk: {buckets: []},
                    type: {buckets: []},
                    category: {buckets: []},
                    urgency: {buckets: []},
                    source: {buckets: []},
                    state: {buckets: []},
                    day: {buckets: []},
                    week: {buckets: []},
                    month: {buckets: []},
                    stage: {buckets: []}
                }
            };
        });

        it('does not throw an error if desk not in deskLookup', function () {
            isoScope.desk = null;

            isoScope.items._aggregations.desk.buckets = [
                {doc_count: 123, key: 'abc123'}
            ];

            desks.deskLookup = {
                otherDesk: {}  // desk abc123 not present in deskLookup
            };

            try {
                facetsInit.resolve();
                isoScope.$digest();
            } catch (ex) {
                fail('A desk not in deskLookup should not cause an error.');
            }
        });

        it('outputs a warning if desk not in deskLookup', function () {
            isoScope.desk = null;

            isoScope.items._aggregations.desk.buckets = [
                {doc_count: 123, key: 'abc123'}
            ];

            desks.deskLookup = {
                otherDesk: {}  // desk abc123 not present in deskLookup
            };

            spyOn(console, 'warn');

            facetsInit.resolve();
            isoScope.$digest();

            expect(console.warn).toHaveBeenCalledWith(
                'Desk (key: abc123) not found in deskLookup, ' +
                'probable storage inconsistency.'
            );
        });
    });

});
