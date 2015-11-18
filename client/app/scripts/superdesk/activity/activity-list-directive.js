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
                single: '=',
                preview: '@'
            },
            templateUrl: asset.templateUrl('superdesk/activity/views/activity-list.html'),
            link: function(scope, elem, attrs) {
                scope.item.actioning = {};

                var intent = {
                    action: scope.action
                };

                if (scope.type) {
                    intent.type = scope.type;
                } else {
                    return;
                }

                var initializeActivities = function(item) {
                    if (!item) {
                        return;
                    }

                    scope.activities = _.filter(superdesk.findActivities(intent, scope.item), function(activity) {
                        if (activity.monitor) {
                            scope.item.actioning = {};
                            scope.item.actioning[activity._id] = false;
                            scope.$watchCollection('item.actioning', function(newValue, oldValue) {
                                if (scope.item.actioning &&
                                    !scope.item.actioning[activity._id] &&
                                    oldValue &&
                                    (newValue[activity._id] !== oldValue[activity._id])) {
                                    if (scope.item.error && scope.item.error.data && scope.item.error.data._message) {
                                        notify.error(gettext(scope.item.error.data._message));
                                        delete scope.item.error;
                                    }
                                }
                            });
                        }

                        return workflowService.isActionAllowed(scope.item, activity.action);
                    });

                    if (scope.preview) {
                        scope.limit = scope.activities.length;
                    } else {
                        scope.limit = scope.activities.length > 6 ? 5 : 6;
                    }

                    // register key shortcuts for single instance of activity list - in preview sidebar
                    if (scope.single) {
                        angular.forEach(scope.activities, function(activity) {
                            if (activity.key) {
                                if (activity.unbind) {
                                    activity.unbind();
                                }
                                activity.unbind = scope.$on('key:' + activity.key, function() {
                                    scope.run(activity);
                                });
                            }
                        });
                    }
                };

                scope.run = function runActivity(activity, e) {
                    if (scope.$root.link(activity._id, scope.item)) {
                        return; // don't try to run it, just let it change url
                    }

                    if (activity.monitor) {
                        scope.item.actioning[activity._id] = true;
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

                scope.$watch('item', initializeActivities);
            }
        };
    }];
});
