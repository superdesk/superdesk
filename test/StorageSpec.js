define([
    'angular-mocks',
    'superdesk/services/storage'
], function() {
    'use strict';

    describe('Storage', function() {
        var storage;

        beforeEach(function() {
            module('superdesk.services');
            inject(function(_storage_) {
                storage = _storage_;
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

        it('can remove item', function() {
            storage.setItem('true', true);
            storage.removeItem('true');
            expect(storage.getItem('true')).toBe(null);
        });
    });
});
