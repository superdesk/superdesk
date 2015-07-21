'use strict';

describe('itemListService', function() {
    beforeEach(module('superdesk.mocks'));
    beforeEach(module('superdesk.itemList'));
    beforeEach(module(function($provide) {
        $provide.service('api', function($q) {
            return function ApiService(endpoint, endpointParam) {
                return {
                    query: function(params) {
                        params._endpoint = endpoint;
                        params._endpointParam = endpointParam;
                        return $q.when(params);
                    }
                };
            };
        });
    }));

    it('can query with default values', inject(function($rootScope, itemListService, api) {
        var queryParams = null;

        itemListService.fetch()
        .then(function(params) {
            queryParams = params;
        });
        $rootScope.$digest();
        expect(queryParams).toEqual({
            _endpoint: 'search',
            _endpointParam: undefined,
            source: {
                query: {
                    filtered: {}
                },
                size: 25,
                from: 0,
                sort: [{_updated: 'desc'}]
            }
        });
    }));

    it('can query with endpoint', inject(function($rootScope, itemListService, api) {
        var queryParams = null;

        itemListService.fetch({
            endpoint: 'archive',
            endpointParam: 'param'
        })
        .then(function(params) {
            queryParams = params;
        });
        $rootScope.$digest();
        expect(queryParams._endpoint).toBe('archive');
        expect(queryParams._endpointParam).toBe('param');
    }));

    it('can query with page', inject(function($rootScope, itemListService, api) {
        var queryParams = null;

        itemListService.fetch({
            pageSize: 15,
            page: 3
        })
        .then(function(params) {
            queryParams = params;
        });
        $rootScope.$digest();
        expect(queryParams.source.size).toBe(15);
        expect(queryParams.source.from).toBe(30);
    }));

    it('can query with sort', inject(function($rootScope, itemListService, api) {
        var queryParams = null;

        itemListService.fetch({
            sortField: '_id',
            sortDirection: 'asc'
        })
        .then(function(params) {
            queryParams = params;
        });
        $rootScope.$digest();
        expect(queryParams.source.sort).toEqual([{_id: 'asc'}]);
    }));

    it('can query with repos', inject(function($rootScope, itemListService, api) {
        var queryParams = null;

        itemListService.fetch({
            repos: ['archive', 'ingest']
        })
        .then(function(params) {
            queryParams = params;
        });
        $rootScope.$digest();
        expect(queryParams.repo).toBe('archive,ingest');
    }));

    it('can query with types', inject(function($rootScope, itemListService, api) {
        var queryParams = null;

        itemListService.fetch({
            types: ['text', 'picture', 'composite']
        })
        .then(function(params) {
            queryParams = params;
        });
        $rootScope.$digest();
        expect(queryParams.source.query.filtered.filter.and[0].terms.type).toEqual(
            ['text', 'picture', 'composite']
        );
    }));

    it('can query with states', inject(function($rootScope, itemListService, api) {
        var queryParams = null;

        itemListService.fetch({
            states: ['spiked', 'published']
        })
        .then(function(params) {
            queryParams = params;
        });
        $rootScope.$digest();
        expect(queryParams.source.query.filtered.filter.and[0].or).toEqual([
            {term: {state: 'spiked'}},
            {term: {state: 'published'}}
        ]);
    }));

    it('can query with notStates', inject(function($rootScope, itemListService, api) {
        var queryParams = null;

        itemListService.fetch({
            notStates: ['spiked', 'published']
        })
        .then(function(params) {
            queryParams = params;
        });
        $rootScope.$digest();
        expect(queryParams.source.query.filtered.filter.and).toEqual([
            {not: {term: {state: 'spiked'}}},
            {not: {term: {state: 'published'}}}
        ]);
    }));

    it('can query with dates', inject(function($rootScope, itemListService, api) {
        var queryParams = null;

        itemListService.fetch({
            creationDateBefore: 1,
            creationDateAfter: 2,
            modificationDateBefore: 3,
            modificationDateAfter: 4
        })
        .then(function(params) {
            queryParams = params;
        });
        $rootScope.$digest();
        expect(queryParams.source.query.filtered.filter.and).toEqual([
            {range: {_created: {lte: 1, gte: 2}}},
            {range: {_updated: {lte: 3, gte: 4}}}
        ]);
    }));

    it('can query with provider, source and urgency', inject(function($rootScope, itemListService, api) {
        var queryParams = null;

        itemListService.fetch({
            provider: 'reuters',
            source: 'reuters_1',
            urgency: 5
        })
        .then(function(params) {
            queryParams = params;
        });
        $rootScope.$digest();
        expect(queryParams.source.query.filtered.filter.and).toEqual([
            {term: {provider: 'reuters'}},
            {term: {source: 'reuters_1'}},
            {term: {urgency: 5}}
        ]);
    }));

    it('can query with headline, subject, keyword, uniqueName and body search',
    inject(function($rootScope, itemListService, api) {
        var queryParams = null;

        itemListService.fetch({
            headline: 'h',
            subject: 's',
            keyword: 'k',
            uniqueName: 'u',
            body: 'b'
        })
        .then(function(params) {
            queryParams = params;
        });
        $rootScope.$digest();
        expect(queryParams.source.query.filtered.query).toEqual({
            query_string: {
                query: 'headline:(*h*) subject.name:(*s*) slugline:(*k*) unique_name:(*u*) body_html:(*b*)',
                lenient: false,
                default_operator: 'AND'
            }
        });
    }));

    it('can query with general search', inject(function($rootScope, itemListService, api) {
        var queryParams = null;

        itemListService.fetch({
            search: 's'
        })
        .then(function(params) {
            queryParams = params;
        });
        $rootScope.$digest();
        expect(queryParams.source.query.filtered.query).toEqual({
            query_string: {
                query: 'headline:(*s*) subject.name:(*s*) slugline:(*s*) unique_name:(*s*) body_html:(*s*)',
                lenient: false,
                default_operator: 'OR'
            }
        });
    }));

    it('can query with saved search', inject(function($rootScope, itemListService, api, $q) {
        var params;
        api.get = angular.noop;
        spyOn(api, 'get').and.returnValue($q.when({filter: {query: {type: '["text"]'}}}));
        itemListService.fetch({
            savedSearch: {_links: {self: {href: 'url'}}}
        }).then(function(_params) {
            params = _params;
        });

        $rootScope.$digest();

        expect(params.source.post_filter.and).toContain({
            terms: {type: ['text']}
        });
    }));
});
