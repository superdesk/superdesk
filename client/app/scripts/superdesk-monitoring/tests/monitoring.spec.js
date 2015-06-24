
describe('monitoring', function() {
    'use strict';

    beforeEach(module('superdesk.monitoring'));

    it('can preview an item', inject(function($controller, $rootScope) {
        var scope = $rootScope.$new(),
            ctrl = $controller('Monitoring', {$scope: scope}),
            item = {};

        expect(ctrl.state['with-preview']).toBeFalsy();

        ctrl.preview(item);

        expect(ctrl.previewItem).toBe(item);
        expect(ctrl.state['with-preview']).toBeTruthy();
    }));
});
