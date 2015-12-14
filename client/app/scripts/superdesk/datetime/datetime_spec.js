define(['superdesk/datetime/datetime'], function() {
    'use strict';

    beforeEach(function() {
        module('superdesk.datetime');
    });

    describe('reldate filter', function() {
        it('can convert js Date into a string', inject(function($filter) {
            var date = new Date();
            expect($filter('reldate')(date)).toBe('a few seconds ago');
        }));
    });

    describe('time filter', function() {
        it('can convert date into time str', inject(function($filter) {
            var date = new Date(2010, 10, 10, 8, 5, 35);
            expect($filter('time')(date)).toBe('8:05');
        }));
    });
});
