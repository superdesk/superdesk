describe('templates', function() {
    'use strict';

    beforeEach(module('superdesk.aggregate.sidebar'));

    describe('aggregate widget controller', function() {
        var scope, ctrl;

        beforeEach(inject(function($rootScope, $controller) {
            scope = $rootScope.$new();
            ctrl = $controller('AggregateCtrl', {$scope: scope});
        }));
        it('can fetch the saved state on init', inject(function(storage) {
            storage.clear();
            expect(ctrl.state).toEqual({});
        }));
        it('can assume unset state is true', inject(function(storage) {
            storage.clear();
            expect(ctrl.getState('test')).toBe(true);
        }));
        it('can switch state', inject(function(storage) {
            storage.clear();
            ctrl.switchState('test');
            expect(ctrl.getState('test')).toBe(false);
            ctrl.switchState('test');
            expect(ctrl.getState('test')).toBe(true);
        }));
        it('can remember state', inject(function($rootScope, $controller) {
            ctrl.switchState('test');
            expect(ctrl.getState('test')).toBe(false);

            scope = $rootScope.$new();
            ctrl = $controller('AggregateCtrl', {$scope: scope});

            expect(ctrl.getState('test')).toBe(false);
        }));
    });
});
