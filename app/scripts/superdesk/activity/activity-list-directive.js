define([
    'lodash'
], function(_) {
    'use strict';

    return ['superdesk', 'activityService', function(superdesk, activityService) {
        return {
            scope: {
                item: '=',
                type: '@',
                action: '@',
                done: '&'
            },
            templateUrl: 'scripts/superdesk/activity/views/activity-list.html',
            link: function(scope, elem, attrs) {
                var intent = {
                    action: scope.action
                };

                if (scope.type) {
                    intent.type = scope.type;
                } else {
                    return;
                }

                scope.activities = superdesk.findActivities(intent);

                scope.run = function runActivity(activity, e) {
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
