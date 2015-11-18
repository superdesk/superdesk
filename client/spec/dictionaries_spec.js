
var openUrl = require('./helpers/utils').open,
    dictionaries = require('./helpers/dictionaries');

describe('DICTIONARIES', function() {
    'use strict';

    describe('add dictionary', function() {
        beforeEach(function() {
            openUrl('/#/settings/dictionaries');
        });

        it('add dictionary', function() {
            dictionaries.addDictionary();
            dictionaries.setName('Test');
            dictionaries.setLanguageId('en');
            dictionaries.save();
            expect(dictionaries.getRow('Test').count()).toBe(1);
        });

        it('add dictionary', function() {
            dictionaries.addPersonalDictionary();
            dictionaries.setLanguageId('en');
            dictionaries.save();
            expect(dictionaries.getPersonalRow('en').isPresent()).toBe(true);
        });
    });

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

        it('add/remove word in dictionary', function() {
            dictionaries.edit('Test 1');
            dictionaries.search('theta');
            expect(dictionaries.getWordsCount()).toBe(0);
            dictionaries.saveWord();
            expect(dictionaries.getWordsCount()).toBe(1);
            dictionaries.removeWord();
            expect(dictionaries.getWordsCount()).toBe(0);
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
