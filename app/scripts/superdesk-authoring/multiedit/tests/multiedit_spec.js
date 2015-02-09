describe('multiedit', function() {
    'use strict';

    beforeEach(module('superdesk.authoring.multiedit'));

    it('can open an item', inject(function(multiEdit) {
        var items = multiEdit.items;
        expect(items.length).toBe(0);
        multiEdit.edit('foo');
        expect(multiEdit.items.length).toBe(1);
        expect(multiEdit.items).not.toEqual(items);
    }));

    it('can remove an item', inject(function(multiEdit) {
        multiEdit.edit('foo');
        multiEdit.edit('bar');
        var items = multiEdit.items;
        multiEdit.remove('foo');
        expect(multiEdit.items.length).toBe(1);
        expect(multiEdit.items).not.toEqual(items);
    }));
});
