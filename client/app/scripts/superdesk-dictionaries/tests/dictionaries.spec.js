
describe('dictionaries', function() {
    'use strict';

    beforeEach(module('superdesk.dictionaries'));

    describe('config modal directive', function() {
        var scope;

        beforeEach(module('templates'));

        beforeEach(inject(function($rootScope, $controller) {
            scope = $rootScope.$new();
            scope.dictionary = {content: {foo: 1, bar: 1}};
            $controller('DictionaryEdit', {$scope: scope});
        }));

        it('can search words', function() {
            scope.filterWords('test');
            expect(scope.isNew).toBe(true);
        });

        it('can add words', function() {
            scope.addWord('test');
            expect(scope.dictionary.content.test).toBe(1);
            expect(scope.words.length).toBe(1);
        });

        it('can remove words', function() {
            scope.filterWords('foo');
            expect(scope.isNew).toBe(false);
            expect(scope.words.length).toBe(1);
            expect(scope.words[0]).toBe('foo');

            scope.removeWord('foo', 'foo');
            expect(scope.isNew).toBe(true);
            expect(scope.words.length).toBe(0);
        });
    });
});
