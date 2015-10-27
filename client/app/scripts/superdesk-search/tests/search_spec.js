'use strict';

describe('search service', function() {
    beforeEach(module('superdesk.templates-cache'));
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
    }));

    it('can create query string query', inject(function($rootScope, search) {
        var criteria = search.query({q: 'test'}).getCriteria();
        expect(criteria.query.filtered.query.query_string.query).toBe('test');
    }));

    it('can create query for from_desk', inject(function($rootScope, search) {
        // only from desk is specified
        var criteria = search.query({from_desk: 'test-authoring'}).getCriteria();
        var filters = criteria.query.filtered.filter.and;
        expect(filters).toContain({term: {'task.last_authoring_desk': 'test'}});
        criteria = search.query({from_desk: 'test-production'}).getCriteria();
        filters = criteria.query.filtered.filter.and;
        expect(filters).toContain({term: {'task.last_production_desk': 'test'}});
    }));

    it('can create query for to_desk', inject(function($rootScope, search) {
        // only to desk is specified
        var criteria = search.query({to_desk: '456-authoring'}).getCriteria();
        var filters = criteria.query.filtered.filter.and;
        expect(filters).toContain({term: {'task.desk': '456'}});
        expect(filters).toContain({exists: {field: 'task.last_production_desk'}});
        criteria = search.query({to_desk: '456-production'}).getCriteria();
        filters = criteria.query.filtered.filter.and;
        expect(filters).toContain({term: {'task.desk': '456'}});
        expect(filters).toContain({exists: {field: 'task.last_authoring_desk'}});
    }));

    it('can create query for from_desk and to_desk', inject(function($rootScope, search) {
        // both from desk and to desk are specified
        var criteria = search.query({from_desk: '123-authoring', to_desk: '456-production'}).getCriteria();
        var filters = criteria.query.filtered.filter.and;
        expect(filters).toContain({term: {'task.last_authoring_desk': '123'}});
        expect(filters).toContain({term: {'task.desk': '456'}});
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
        'superdesk.templates-cache' // needed so that directive's template is placed into
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
        spyOn(desks, 'initialize').and.returnValue($q.when([]));

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
                    priority: {buckets: []},
                    source: {buckets: []},
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
