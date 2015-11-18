'use strict';

describe('ContentFiltersConfigCtrl', function() {
    var ctrl;

    beforeEach(module('superdesk.content_filters'));

    beforeEach(inject(function($controller) {
        ctrl = $controller('ContentFiltersConfigCtrl', {});
    }));

    describe('on instantiation', function () {
        it('assigns the correct value to TEMPLATES_DIR variable', function () {
            expect(ctrl.TEMPLATES_DIR).toEqual(
                'scripts/superdesk-content-filters/views'
            );
        });

        it('initializes active tab name to "filters"', function () {
            expect(ctrl.activeTab).toEqual('filters');
        });
    });

    describe('changeTab() method', function () {
        it('changes the active tab name to given name', function () {
            ctrl.activeTab = 'foo';
            ctrl.changeTab('bar');
            expect(ctrl.activeTab).toEqual('bar');
        });
    });

});
