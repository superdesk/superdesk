define([
    'lodash'
], function(_) {
    'use strict';

    return ['superdesk', function(superdesk) {
        return {
            scope: {
                data: '=',
                type: '@',
                action: '@',
                done: '='
            },
            template: '<li ng-repeat="activity in activities" sd-activity-item></li>',
            link: function(scope, elem, attrs) {
                var intent = {
                    action: scope.action
                };

                if (!scope.type && scope.data.href) { // guess item type by self href
                    //intent.type = scope.data._links.self.href.split('/')[1];
                    intent.type = scope.data.href.split('/')[1];
                } else if (scope.type) {
                    intent.type = scope.type;
                } else {
                    return;
                }

                scope.activities = superdesk.findActivities(intent);
            }
        };
    }];
});
