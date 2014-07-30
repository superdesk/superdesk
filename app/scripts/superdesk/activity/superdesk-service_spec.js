define([
    './superdesk-service',
    './activity',
    'angular-route'
], function(superdeskProvider) {
    'use strict';

    describe('Superdesk service', function() {
        var provider;
        var isBeta = false;
        var intent = {action: 'testAction', type: 'testType'};
        var testWidget = {testData: 123};
        var testPane = {testData: 123};
        var testActivity = {
            label: 'test',
            controller: function() {
                return 'test';
            },
            filters: [intent]
        };

        beforeEach(function() {
            module('ngRoute');
            module('superdesk.activity');
            module(function($provide) {
                $provide.service('gettext', function() {});
                $provide.service('modal', function() {});
                $provide.service('betaService', function() {
                    this.isBeta = function() { return isBeta; };
                });
                $provide.service('DataAdapter', function() {});

                provider = $provide.provider('superdesk', superdeskProvider);
                provider.widget('testWidget', testWidget);
                provider.pane('testPane', testPane);
                provider.activity('testActivity', testActivity);
            });
        });

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
    });
});
