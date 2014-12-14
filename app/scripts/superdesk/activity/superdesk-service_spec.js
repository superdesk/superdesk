(function() {
    'use strict';

    describe('Superdesk service', function() {
        var provider;
        var intent = {action: 'testAction', type: 'testType'};
        var testWidget = {testData: 123};
        var testPane = {testData: 123};
        var testActivity = {
            label: 'test',
            controller: function() {
                return 'test';
            },
            filters: [intent],
            category: 'superdesk.menu.main'
        };

        angular.module('superdesk.activity.test', ['superdesk.activity'])
            .config(function(superdeskProvider) {
                provider = superdeskProvider;
                provider.widget('testWidget', testWidget);
                provider.pane('testPane', testPane);
                provider.activity('testActivity', testActivity);
                provider.activity('missingFeatureActivity', {
                    category: superdeskProvider.MENU_MAIN,
                    features: {missing: 1},
                    filters: [{action: 'test', type: 'features'}]
                });
                provider.activity('missingPrivilegeActivity', {
                    category: superdeskProvider.MENU_MAIN,
                    privileges: {missing: 1},
                    filters: [{action: 'test', type: 'privileges'}]
                });
            });

        beforeEach(module('superdesk.activity'));
        beforeEach(module('superdesk.activity.test'));
        beforeEach(module('superdesk.mocks'));

        it('exists', inject(function(superdesk) {
            expect(superdesk).toBeDefined();
        }));

        it('can add widgets', inject(function(superdesk) {
            expect(superdesk.widgets.testWidget.testData).toBe(testWidget.testData);
        }));

        it('can add panes', inject(function(superdesk) {
            expect(superdesk.panes.testPane.testData).toBe(testPane.testData);
        }));

        it('can add activities', inject(function(superdesk) {
            expect(superdesk.activities.testActivity.label).toBe(testActivity.label);
        }));

        it('can run activities', inject(function($rootScope, superdesk, activityService) {
            var result = null;

            activityService.start(superdesk.activities.testActivity)
            .then(function(res) {
                result = res;
            });

            $rootScope.$digest();

            expect(result).toBe('test');
        }));

        it('can run activities by intent', inject(function($rootScope, superdesk) {
            var successResult = null;
            var failureResult = null;

            superdesk.intent('testAction', 'testType', 'testData')
            .then(function(result) {
                successResult = result;
            });
            superdesk.intent('testAction2', 'testType2', 'testData2')
            .then(function() {}, function(result) {
                failureResult = result;
            });

            $rootScope.$digest();

            expect(successResult).toBe('test');
            expect(failureResult).toBe(undefined);
        }));

        it('can find activities', inject(function(superdesk) {
            var success = superdesk.findActivities(intent);
            var failure = superdesk.findActivities({type: 'testType2', action: 'testAction2'});

            expect(success.length).toBe(1);
            expect(success[0].label).toBe('test');
            expect(failure.length).toBe(0);
        }));

        it('can check features required by activity', inject(function(superdesk, features) {
            var list = superdesk.findActivities({type: 'features', action: 'test'});
            expect(list.length).toBe(0);
        }));

        it('can filter activities based on privileges', inject(function(superdesk, privileges) {
            var list = superdesk.findActivities({type: 'privileges', action: 'test'});
            expect(list.length).toBe(0);

            privileges.setUserPrivileges({missing: 1});
            list = superdesk.findActivities({type: 'privileges', action: 'test'});
            expect(list.length).toBe(1);
        }));

        it('can get main menu and filter out based on features/permissions', inject(function(superdesk, $rootScope) {

            var menu;
            superdesk.getMenu(superdesk.MENU_MAIN).then(function(_menu) {
                menu = _menu;
            });

            $rootScope.$digest();
            expect(menu.length).toBe(1);
        }));
    });
})();
