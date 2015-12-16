(function() {
    'use strict';

    describe('widgets provider', function() {
        var dashboardWidgetsProvider;

        beforeEach(function() {

            angular.module('superdesk.dashboard.widgets.tests', [])
            .config(['dashboardWidgetsProvider', function(_dashboardWidgetsProvider_) {
                dashboardWidgetsProvider = _dashboardWidgetsProvider_;
            }]);

            module('superdesk.dashboard.widgets', 'superdesk.dashboard.widgets.tests');

            // init the tests module to get the actual provider
            inject(function(){});
        });

        beforeEach(function() {
            dashboardWidgetsProvider.addWidget('id', {label: 'first'}, 'true');
            dashboardWidgetsProvider.addWidget('id', {label: 'second'}, 'true');
        });

        it('is defined', inject(function(dashboardWidgets) {
            expect(dashboardWidgets).not.toBe(undefined);
        }));

        it('can register widgets', inject(function(dashboardWidgets) {
            expect(dashboardWidgets.length).toBe(1);
            expect(dashboardWidgets[0]._id).toBe('id');
            expect(dashboardWidgets[0].label).toBe('second');
        }));
    });
})();
