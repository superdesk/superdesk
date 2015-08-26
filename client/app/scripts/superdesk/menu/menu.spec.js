
'use strict';

describe('superdesk.menu', function() {
    beforeEach(module('superdesk.menu'));

    it('has flags', inject(function($controller) {
        var ctrl = $controller('SuperdeskCtrl', {});
        expect(ctrl.flags.menu).toBe(false);
    }));
});
