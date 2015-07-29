
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
    });
});
