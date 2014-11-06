'use strict';

describe('content query builder', function() {
    beforeEach(module('superdesk.archive'));

    it('can create base query', inject(function(contentQuery) {
        var query = contentQuery.query();
        var criteria = query.getCriteria();
        var filters = criteria.query.filtered.filter.and;
        expect(filters).toContain({not: {term: {is_spiked: true}}});
        expect(criteria.sort).toContain({versioncreated: 'desc'});
        expect(criteria.size).toBe(25);
    }));

    it('can create query string query', inject(function(contentQuery) {
        var query = contentQuery.query('test');
        var criteria = query.getCriteria();
        expect(criteria.query.filtered.query.query_string.query).toBe('test');

        criteria = contentQuery.query().q('foo').getCriteria();
        expect(criteria.query.filtered.query.query_string.query).toBe('foo');
    }));

    it('can set size', inject(function(contentQuery) {
        var criteria = contentQuery.query().size(10).getCriteria();
        expect(criteria.size).toBe(10);
    }));
});
