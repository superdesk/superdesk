define([
    'lodash'
], function(_) {
    'use strict';

    return ['superdesk', 'activityService', 'workflowService', 'asset', 'notify',
    function(superdesk, activityService, workflowService, asset, notify) {
        return {
            scope: {
                item: '=',
                type: '@',
                action: '@',
                done: '&',
                single: '='
            },
            templateUrl: asset.templateUrl('superdesk/activity/views/activity-list.html'),
            link: function(scope, elem, attrs) {
                scope.item.actioning = '';

                var intent = {
                    action: scope.action
                };

                if (scope.type) {
                    intent.type = scope.type;
                } else {
                    return;
                }

                scope.activities = _.filter(superdesk.findActivities(intent, scope.item), function(activity) {

                    if (activity.monitor) {
                        scope.$watch('item.actioning', function(newValue, oldValue) {
                            if (scope.item.actioning === '') {
                                    if (scope.item.error) {
                                        notify.error(gettext(scope.item.error.data._message));
                                    }
                                }
                        });
                    }

                    return workflowService.isActionAllowed(scope.item, activity.action);
                });

                scope.run = function runActivity(activity, e) {
                    if (scope.$root.link(activity._id, scope.item)) {
                        return; // don't try to run it, just let it change url
                    }

					if (activity.monitor) {
                        scope.item.actioning = 'actioning';
                    }

                    if (e != null) {
                        e.stopPropagation();
                    }

                    activityService.start(activity, {data: {item: scope.item}})
                        .then(function() {
                            if (typeof scope.done === 'function') {
                                scope.done(scope.data);
                            }
                        });

                };

                // register key shortcuts for single instance of activity list - in preview sidebar
                if (scope.single) {
                    angular.forEach(scope.activities, function(activity) {
                        if (activity.key) {
                            scope.$on('key:' + activity.key, function() {
                                scope.run(activity);
                            });
                        }
                    });
                }
            }
        };
    }];
});
