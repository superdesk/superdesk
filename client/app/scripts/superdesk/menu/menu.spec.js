
'use strict';

describe('superdesk.menu', function() {
    beforeEach(module('superdesk.menu'));

    it('has flags', inject(function(superdeskFlags) {
        expect(superdeskFlags.flags.menu).toBe(false);
    }));
});
