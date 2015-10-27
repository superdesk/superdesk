describe('monitoring', function() {
    'use strict';

    beforeEach(module('superdesk.monitoring'));

    it('can preview an item', inject(function($controller, $rootScope) {
        var scope = $rootScope.$new(),
            ctrl = $controller('Monitoring', {$scope: scope}),
            item = {};

        expect(ctrl.state['with-preview']).toBeFalsy();

        ctrl.preview(item);

        expect(ctrl.previewItem).toBe(item);
        expect(ctrl.state['with-preview']).toBeTruthy();

        ctrl.closePreview();
        expect(ctrl.previewItem).toBe(null);
        expect(ctrl.state['with-preview']).toBeFalsy();
    }));

    it('can edit item', inject(function($controller, $rootScope) {
        var scope = $rootScope.$new(),
            ctrl = $controller('Monitoring', {$scope: scope}),
            item = {};

        expect(ctrl.state['with-authoring']).toBeFalsy();

        ctrl.edit(item);
        expect(ctrl.editItem).toBe(item);
        expect(ctrl.state['with-authoring']).toBeTruthy();
    }));

    describe('cards service', function() {
        it('can get criteria for stage', inject(function(cards) {
            var card = {_id: '123'};
            var criteria = cards.criteria(card);
            expect(criteria.source.query.filtered.filter.and).toContain({
                term: {'task.stage': card._id}
            });

            criteria = cards.criteria(card, 'foo');
            expect(criteria.source.query.filtered.filter.and).toContain({
                query: {query_string: {query: 'foo', lenient: false}}
            });
        }));

        it('can get criteria for personal', inject(function(cards, session) {
            var card = {type: 'personal'};
            session.identity = {_id: 'foo'};
            var criteria = cards.criteria(card);
            expect(criteria.source.query.filtered.filter.and).toContain({
                bool: {
                    must: {term: {original_creator: session.identity._id}},
                    must_not: {exists: {field: 'task.desk'}}
                }
            });
        }));

        it('can get criteria for saved search', inject(function(cards) {
            var card = {type: 'search', search: {filter: {query: {q: 'foo'}}}};
            var criteria = cards.criteria(card);
            expect(criteria.source.query.filtered.query.query_string.query).toBe('foo');
        }));

        it('can get criteria for spike desk', inject(function(cards) {
            var card = {type: 'spike'};
            var criteria = cards.criteria(card);
            expect(criteria.source.query.filtered.filter.and).toContain({
                term: {'task.desk': card._id}
            });
            expect(criteria.source.query.filtered.filter.and).toContain({
                term: {'state': 'spiked'}
            });
        }));

        it('can get criteria for highlight', inject(function(cards) {
            var card = {type: 'highlights'};
            var queryParam = {highlight: '123'};
            var criteria = cards.criteria(card, null, queryParam);
            expect(criteria.source.query.filtered.filter.and).toContain({
                and: [{term: {'highlights': queryParam.highlight}}]
            });
        }));

        it('can get criteria for stage with search', inject(function(cards) {
            var card = {_id: '123', query: 'test'};
            var criteria = cards.criteria(card);
            expect(criteria.source.query.filtered.query.query_string.query).toBe('test');
        }));

        it('can get criteria for personal with search', inject(function(cards, session) {
            var card = {type: 'personal', query: 'test'};
            session.identity = {_id: 'foo'};
            var criteria = cards.criteria(card);
            expect(criteria.source.query.filtered.query.query_string.query).toBe('test');
        }));

        it('can get criteria for spike with search', inject(function(cards) {
            var card = {_id: '123', type: 'spike', query: 'test'};
            var criteria = cards.criteria(card);
            expect(criteria.source.query.filtered.query.query_string.query).toBe('test');
        }));

        it('can get criteria for highlight with search', inject(function(cards) {
            var card = {type: 'highlights', query: 'test'};
            var queryParam = {highlight: '123'};
            var criteria = cards.criteria(card, null, queryParam);
            expect(criteria.source.query.filtered.query.query_string.query).toBe('test');
        }));

        it('can get criteria for file type filter', inject(function(cards) {
            var card = {_id: '123', fileType: JSON.stringify(['text'])};
            var criteria = cards.criteria(card);
            expect(criteria.source.query.filtered.filter.and).toContain({
                terms: {type: ['text']}
            });
        }));

        it('can get criteria for saved search with search', inject(function(cards) {
            var card = {_id: '123', type: 'search', query: 'test',
                        search: {filter: {query: {q: 'foo', type: '[\"picture\"]'}}}
            };
            var criteria = cards.criteria(card);
            expect(criteria.source.query.filtered.query.query_string.query).toBe('(test) foo');
            expect(criteria.source.post_filter.and).toContain({terms: {type: ['picture']}});
        }));

        it('can get criteria for file type filter with search', inject(function(cards) {
            var card = {_id: '123', fileType: JSON.stringify(['text']), query: 'test'};
            var criteria = cards.criteria(card);
            expect(criteria.source.query.filtered.filter.and).toContain({
                terms: {type: ['text']}
            });
        }));

        it('can get criteria for multiple file type filter', inject(function(cards) {
            var card = {_id: '123', fileType: JSON.stringify(['text', 'picture'])};
            var criteria = cards.criteria(card);
            expect(criteria.source.query.filtered.filter.and).toContain({
                terms: {type: ['text', 'picture']}
            });
        }));
    });

    describe('monitoring group directive', function() {

        beforeEach(module('superdesk.templates-cache'));

        beforeEach(inject(function($templateCache) {
            // change template not to require aggregate config but rather render single group
            $templateCache.put('scripts/superdesk-monitoring/views/monitoring-view.html',
                '<div id="group" sd-monitoring-group data-group="{type: \'stage\', _id: \'foo\'}"></div>');
        }));

        it('can update items on content:update event',
        inject(function($rootScope, $compile, $q, api, $timeout) {
            var scope = $rootScope.$new();
            $compile('<div sd-monitoring-view></div>')(scope);
            scope.$digest();

            spyOn(api, 'query').and.returnValue($q.when({_items: [], _meta: {total: 0}}));
            scope.$broadcast('content:update', {stages: {'bar': 1}});
            scope.$digest();
            $timeout.flush(500);
            expect(api.query).not.toHaveBeenCalled();

            scope.$broadcast('content:update', {stages: {'foo': 1}});
            scope.$digest();
            $timeout.flush(500);
            expect(api.query).toHaveBeenCalled();
        }));

        it('can generate unique track by id', inject(function($rootScope, $compile) {
            var scope = $rootScope.$new(),
                $elm = $compile('<div sd-monitoring-view></div>')(scope);
            scope.$digest();

            var sdGroupElement = $elm.find('#group'),
                iScope = sdGroupElement.isolateScope(),
                item = {state: 'ingested', _id: '123', '_current_version': 'dddd'};

            expect(iScope.uuid(item)).toBe('123');
            item = {state: 'foo', _id: 'test', _current_version: '123'};
            expect(iScope.uuid(item)).toBe('test:123');
        }));

        it('can edit non spiked item', inject(function($controller, $rootScope, $compile, authoringWorkspace) {
            var scope = $rootScope.$new(),
                $elm = $compile('<div sd-monitoring-view></div>')(scope);
            scope.$digest();
            spyOn(authoringWorkspace, 'edit');

            var sdGroupElement = $elm.find('#group'),
                iScope = sdGroupElement.isolateScope(),
                item1 = {state: 'spiked'},
                item2 = {state: 'fetched'};

            iScope.edit(item1, true);
            expect(authoringWorkspace.edit).not.toHaveBeenCalled();

            iScope.edit(item2, true);
            expect(authoringWorkspace.edit).toHaveBeenCalled();
        }));
    });
});
