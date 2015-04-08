
var openUrl = require('./helpers/utils').open,
    dictionaries = require('./helpers/dictionaries');

describe('DICTIONARIES', function() {
    'use strict';

    describe('edit dictionary', function() {
        beforeEach(function() {
            openUrl('/#/settings/dictionaries');
        });

        it('change dictionary name', function() {
            dictionaries.edit('Test 1');
            dictionaries.setName('Test 2');
            dictionaries.save();
            expect(dictionaries.getRow('Test 2').count()).toBe(1);
            expect(dictionaries.getRow('Test 1').count()).toBe(0);
        });

        it('add a word to dictionary', function() {
            dictionaries.edit('Test 1');
            dictionaries.addWord('theta');
            dictionaries.saveWord();
            expect(dictionaries.getWord().getText()).toBe('');
            dictionaries.getAddWordButton().isEnabled().then(
                function(enabled) { expect(enabled).toBe(false); }
            );
        });
    });

    describe('delete dictionary', function() {
        beforeEach(function() {
            openUrl('/#/settings/dictionaries');
        });

        it('delete dictionary', function() {
            expect(dictionaries.getRow('Test 1').count()).toBe(1);
            dictionaries.remove('Test 1');
            expect(dictionaries.getRow('Test 1').count()).toBe(0);
        });
    });
});
