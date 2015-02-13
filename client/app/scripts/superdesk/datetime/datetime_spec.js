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
});
