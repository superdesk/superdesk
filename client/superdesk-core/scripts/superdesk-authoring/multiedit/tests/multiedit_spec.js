describe('multiedit', function() {
    'use strict';

    beforeEach(function() {
        localStorage.clear();
    });

    beforeEach(module('superdesk.authoring.multiedit'));

    it('can open an item', inject(function(multiEdit) {
        var items = multiEdit.items;
        expect(items.length).toBe(0);
        multiEdit.edit('foo', 0);
        expect(multiEdit.items.length).toBe(1);
        expect(multiEdit.items).toEqual(items);
    }));

    it('can remove an item from a board', inject(function(multiEdit) {
        multiEdit.edit('foo', 0);
        multiEdit.edit('bar', 1);
        var items = multiEdit.items;
        multiEdit.remove('foo');
        expect(multiEdit.items.length).toBe(2);
        expect(multiEdit.items).toEqual(items);
    }));

    it('can remove borad', inject(function(multiEdit) {
        multiEdit.edit('foo', 0);
        multiEdit.edit('bar', 1);
        multiEdit.edit('joe', 2);
        multiEdit.close(1);
        expect(multiEdit.items.length).toBe(2);
    }));
});
