'use strict';

describe('search service', function() {
    beforeEach(module('templates'));
    beforeEach(module('superdesk.search'));

    it('can create base query', inject(function(search) {
        var query = search.query();
        var criteria = query.getCriteria();
        var filters = criteria.query.filtered.filter.and;
        expect(filters).toContain({not: {term: {state: 'spiked'}}});
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
