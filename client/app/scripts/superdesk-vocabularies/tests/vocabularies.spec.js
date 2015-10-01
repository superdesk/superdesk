
describe('vocabularies', function() {
    'use strict';

    beforeEach(module('superdesk.vocabularies'));
    beforeEach(module('superdesk.authoring'));
    beforeEach(module('templates'));

    it('can fetch vocabularies', inject(function(api, vocabularies, $q, $rootScope) {
        var fixture = {foo: 'bar'};
        spyOn(api, 'query').and.returnValue($q.when(fixture));
        var result;
        vocabularies.getVocabularies().then(
            function(vocabs) {
                result = vocabs;
            }
        );
        $rootScope.$digest();
        expect(api.query).toHaveBeenCalledWith('vocabularies');
        expect(result).toBe(fixture);
        expect(vocabularies.vocabularies).toBe(fixture);
    }));

    describe('config modal', function() {

        describe('model', function() {
            var scope;

            beforeEach(inject(function($rootScope, $controller) {
                scope = $rootScope.$new();
                scope.vocabulary = {items: [
                    {foo: 'flareon', bar: 'beedrill'},
                    {bar: 'bellsprout', spam: 'sandslash'},
                    {qux: 'quagsire', foo: 'frillish', corge: 'corfish'}
                ]};
                $controller('VocabularyEdit', {$scope: scope});
            }));

            it('being detected correctly', function() {
                expect(scope.model).toEqual(
                    {foo: null, bar: null, spam: null, qux: null, corge: null}
                );
            });
        });

        describe('controller', function() {
            var scope;
            var testItem;

            beforeEach(inject(function($rootScope, $controller) {
                scope = $rootScope.$new();
                testItem = {foo: 'flareon', bar: 'beedrill'};
                scope.vocabulary = {items: [testItem]};
                $controller('VocabularyEdit', {$scope: scope});
            }));

            it('can add items', function() {
                scope.addItem();
                expect(scope.vocabulary.items.length).toBe(2);
                expect(scope.vocabulary.items[1]).toEqual({foo: null, bar: null});
            });

            it('can remove items', function() {
                var testItem2 = {foo: 'flaaffy', bar: 'bidoof'};
                scope.vocabulary.items.push(testItem2);
                scope.removeItem(testItem);
                expect(scope.vocabulary.items.length).toBe(1);
                expect(scope.vocabulary.items[0]).toEqual(testItem2);
                scope.removeItem(testItem2);
                expect(scope.vocabulary.items.length).toBe(0);
            });

            it('can save vocabulary', inject(function(api, $q, $rootScope, metadata) {
                scope.vocabulary.items[0].foo = 'feraligatr';
                scope.vocabulary.items[0].bar = 'bayleef';
                spyOn(api, 'save').and.returnValue($q.when());
                spyOn(metadata, 'initialize').and.returnValue($q.when());
                scope.save();
                $rootScope.$digest();
                expect(api.save).toHaveBeenCalledWith('vocabularies', {
                    items: [{foo: 'feraligatr', bar: 'bayleef'}]
                });
                expect(metadata.initialize).toHaveBeenCalled();
            }));

            it('can cancel editing vocabulary', inject(function(api, $q, $rootScope, metadata) {
                var vocabularyLink = scope.vocabulary;
                scope.vocabulary.items[0].foo = 'furret';
                scope.vocabulary.items[0].bar = 'buizel';
                scope.cancel();
                $rootScope.$digest();
                expect(vocabularyLink).toEqual({
                    items: [{foo: 'flareon', bar: 'beedrill'}]
                });
            }));
        });
    });
});
