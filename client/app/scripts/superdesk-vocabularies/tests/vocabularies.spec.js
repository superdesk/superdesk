
describe('vocabularies', function() {
    'use strict';

    beforeEach(module('superdesk.vocabularies'));
    beforeEach(module('superdesk.authoring'));
    beforeEach(module('templates'));

    it('can fetch vocabularies', inject(function(api, vocabularies, $q, $rootScope) {
        spyOn(api, 'query').and.returnValue($q.when());
        var scope = $rootScope.$new();
        vocabularies.getVocabularies(scope);
        $rootScope.$digest();
        expect(api.query).toHaveBeenCalledWith('vocabularies');
    }));

    describe('config modal directive', function() {
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
            scope.addItem();
            scope.removeItem(testItem);
            expect(scope.vocabulary.items.length).toBe(1);
            expect(scope.vocabulary.items[0]).toEqual({foo: null, bar: null});
            scope.removeItem({foo: null, bar: null});
            expect(scope.vocabulary.items.length).toBe(0);
        });

        it('can save vocabulary', inject(function(api, $q, $rootScope) {
            scope.addItem();
            scope.vocabulary.items[1].foo = 'feraligatr';
            scope.vocabulary.items[1].bar = 'bayleef';
            scope.closeVocabulary = function() {};
            spyOn(api, 'save').and.returnValue($q.when());
            spyOn(scope, 'closeVocabulary').and.returnValue($q.when());
            scope.save();
            $rootScope.$digest();
            expect(api.save).toHaveBeenCalledWith('vocabularies', {
                items: [
                    {foo: 'flareon', bar: 'beedrill'},
                    {foo: 'feraligatr', bar: 'bayleef'}
                ]
            });
        }));
    });
});
