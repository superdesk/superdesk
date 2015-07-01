
describe('text editor', function() {
    'use strict';
    beforeEach(module('superdesk.editor'));
    it('can prevent input events on elem', inject(function(editor) {
        var p = document.createElement('p'),
            handler = jasmine.createSpy('test');

        document.body.appendChild(p);
        p.contentEditable = true;
        p.textContent = 'foo';
        p.focus();

        editor.addEventListeners(p);
        p.addEventListener('input', handler);

        editor.stopEvents = true;
        expect(document.execCommand('insertHTML', false, 'bar')).toBeTruthy();
        expect(handler).not.toHaveBeenCalled();

        editor.stopEvents = false;
        expect(document.execCommand('insertHTML', false, 'baz')).toBeTruthy();
        expect(handler).toHaveBeenCalled();

        editor.removeEventListeners(p);
        expect(document.execCommand('insertHTML', false, 'baz')).toBeTruthy();
        expect(handler.calls.count()).toBe(2);
    }));
});
