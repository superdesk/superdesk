define([
    'angular',
    'superdesk/storage',
    'angular-mocks'
], function(angular) {
    'use strict';

    describe('Storage', function() {
        var storage, storageFactory;

        beforeEach(function() {
            module('superdesk.storage');
            inject(function(_storage_) {
                storage = new _storage_;
                storageFactory = _storage_;
            });

            storage.clear();
        });

        it('can clear', function() {
            storage.setItem('test', 'test');
            storage.clear();
            expect(storage.getItem('test')).toBe(null);
        });

        it('can save text', function() {
            storage.setItem('test', 'text');
            expect(storage.getItem('test')).toBe('text');
        });

        it('can save objects', function() {
            var data = {id: 1, name: 'test'};
            storage.setItem('test', data);
            expect(storage.getItem('test')).toEqual(data);
        });

        it('can save boolean', function() {
            storage.setItem('true', true);
            expect(storage.getItem('true')).toBe(true);

            storage.setItem('false', false);
            expect(storage.getItem('false')).toBe(false);
        });

        it('can define namespaces', function() {
            var storage2 = new storageFactory('x');
            storage2.clear();
            storage.setItem('test', 'test');
            expect(storage2.getItem('test')).toBe(null);
        });
    });
});