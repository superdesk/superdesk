define([
    'lodash'
], function(_) {
    'use strict';

    return ['superdesk', 'activityService', 'workflowService', 'asset', function(superdesk, activityService, workflowService, asset) {
        return {
            scope: {
                item: '=',
                type: '@',
                action: '@',
                done: '&'
            },
            templateUrl: asset.templateUrl('superdesk/activity/views/activity-list.html'),
            link: function(scope, elem, attrs) {
                var intent = {
                    action: scope.action
                };

                if (scope.type) {
                    intent.type = scope.type;
                } else {
                    return;
                }

                scope.activities = _.filter(superdesk.findActivities(intent, scope.item), function(activity) {
                    return workflowService.isActionAllowed(scope.item, activity.action);
                });

                scope.run = function runActivity(activity, e) {
                    if (scope.$root.link(activity._id, scope.item)) {
                        return; // don't try to run it, just let it change url
                    }

                    e.stopPropagation();
                    activityService.start(activity, {data: {item: scope.item}})
                        .then(function() {
                            if (typeof scope.done === 'function') {
                                scope.done(scope.data);
                            }
                        });
                };
            }
        };
    }];
});
