
describe('production', function() {
    'use strict';

    beforeEach(module('superdesk.production'));

    it('can toggle display mode', inject(function($controller, $rootScope) {
        var scope = $rootScope.$new(),
            ctrl = $controller('Production', {$scope: scope});

        expect(ctrl.view.max).toBeTruthy();

        ctrl.openItem();
        expect(ctrl.view.medium).toBeTruthy();
        expect(ctrl.view.max).toBeFalsy();

        ctrl.closeList();
        expect(ctrl.view.min).toBeTruthy();
        expect(ctrl.view.medium).toBeFalsy();
        expect(ctrl.view.max).toBeFalsy();

        ctrl.openList();
        expect(ctrl.view.medium).toBeTruthy();
        expect(ctrl.view.min).toBeFalsy();
        expect(ctrl.view.max).toBeFalsy();

        ctrl.compactView();
        expect(ctrl.view.compact).toBeTruthy();
        expect(ctrl.view.medium).toBeFalsy();

        ctrl.closeList();
        ctrl.openList();
        expect(ctrl.view.compact).toBeTruthy();
        expect(ctrl.view.medium).toBeFalsy();

        ctrl.extendedView();
        expect(ctrl.view.medium).toBeTruthy();
        expect(ctrl.view.compact).toBeFalsy();

        ctrl.closeEditor();
        expect(ctrl.view.max).toBeTruthy();
        expect(ctrl.view.min).toBeFalsy();
        expect(ctrl.view.compact).toBeFalsy();
        expect(ctrl.view.medium).toBeFalsy();

        ctrl.openItem();
        expect(ctrl.view.medium).toBeTruthy();
        expect(ctrl.view.min).toBeFalsy();
        expect(ctrl.view.max).toBeFalsy();
        expect(ctrl.view.compact).toBeFalsy();

        ctrl.closeItem();
        expect(ctrl.view.max).toBeTruthy();
        expect(ctrl.view.min).toBeFalsy();
        expect(ctrl.view.medium).toBeFalsy();
        expect(ctrl.view.compact).toBeFalsy();
    }));
});
