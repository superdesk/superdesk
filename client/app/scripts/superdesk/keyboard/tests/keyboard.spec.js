'use strict';

describe('keyboardManager', function() {

    beforeEach(module('superdesk.keyboard'));

    var km, elem, $timeout,
        options = {inputDisabled: false};

    function keydown(label, code) {
        var e = $.Event('keydown');
        e.which = code;
        elem.trigger(e);
        km.keyboardEvent[label].callback(e);
        $timeout.flush(100);
    }

    beforeEach(inject(function($injector) {
        $timeout = $injector.get('$timeout');
        km = $injector.get('keyboardManager');
        elem = $('<input type="text" />');
    }));

    it('can bind and unbind', function() {
        var status = false;

        km.bind('up', function() {
            status = true;
        }, options);

        expect(status).toBe(false);

        keydown('up', 38);

        expect(status).toBe(true);

        km.unbind('up');

        expect(km.keyboardEvent.up).toBe(undefined);
    });

    it('can push and pop an event', function() {
        var from;

        km.push('up', function() {
            from = '1';
        }, options);

        km.push('up', function() {
            from = '2';
        }, options);

        keydown('up', 38);

        expect(from).toBe('2');

        km.pop('up');

        keydown('up', 38);

        expect(from).toBe('1');

        km.pop('up');

        keydown('up', 38);

        expect(from).toBe('1'); // no change
    });

    it('can broadcast keydown events', inject(function($rootScope, $document) {
        var handler = jasmine.createSpy('handler');
        $rootScope.$on('key:t', handler);

        var e = $.Event('keydown');
        e.which = 't'.charCodeAt(0);
        $(document.body).trigger(e);

        $rootScope.$digest();
        expect(handler).toHaveBeenCalled();
    }));

    it('can broadcast ctrl+key events', inject(function($rootScope, $document) {
        var handler = jasmine.createSpy('handler');
        $rootScope.$on('key:ctrl:t', handler);

        var e = $.Event('keydown');
        e.which = 't'.charCodeAt(0);
        e.ctrlKey = true;
        $(document.body).trigger(e);

        $rootScope.$digest();
        expect(handler).toHaveBeenCalled();
    }));
});
