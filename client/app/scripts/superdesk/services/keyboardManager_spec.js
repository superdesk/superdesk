define([
    'jquery',
    './keyboardManager'
], function($, kbManager) {
    'use strict';

    describe('keyboardManager', function() {

        beforeEach(module(kbManager.name));

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
    });
});
