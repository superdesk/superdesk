describe('templates', function() {
    'use strict';

    beforeEach(module('superdesk.aggregate'));

    describe('aggregate widget controller', function() {
        var scope, ctrl;

        beforeEach(inject(function($rootScope, $controller) {
            scope = $rootScope.$new();
            ctrl = $controller('AggregateCtrl', {$scope: scope});
        }));
        it('can fetch the saved expanded state on init', inject(function(storage) {
            storage.clear();
            expect(ctrl.state.expanded).toEqual({});
        }));
        it('can assume unset expanded state is true', inject(function(storage) {
            storage.clear();
            expect(ctrl.getExpandedState('test')).toBe(true);
        }));
        it('can switch expanded state', inject(function(storage) {
            storage.clear();
            ctrl.switchExpandedState('test');
            expect(ctrl.getExpandedState('test')).toBe(false);
            ctrl.switchExpandedState('test');
            expect(ctrl.getExpandedState('test')).toBe(true);
        }));
        it('can remember expanded state', inject(function($rootScope, $controller) {
            ctrl.switchExpandedState('test');
            expect(ctrl.getExpandedState('test')).toBe(false);

            scope = $rootScope.$new();
            ctrl = $controller('AggregateCtrl', {$scope: scope});

            expect(ctrl.getExpandedState('test')).toBe(false);
        }));
        it('can set solo group', inject(function(storage) {
            storage.clear();
            ctrl.setSoloGroup({_id: 'test'});
            expect(ctrl.state.solo._id).toBe('test');
        }));
        it('can remember solo group', inject(function() {
            expect(ctrl.state.solo._id).toBe('test');
        }));
    });
});
