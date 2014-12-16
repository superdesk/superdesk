define([
], function() {
    'use strict';

    return ['activityService', function(activityService) {
        return {
            replace: true,
            template: [
                '<li class="item-field" ng-click="run(activity, $event)" title="{{ :: activity.label | translate }}">',
                '<button><i class="icon-{{ :: activity.icon }}" ng-show=":: activity.icon"></i>',
                '<span>{{ :: activity.label | translate }}</span></button>',
                '</li>'
            ].join(''),
            link: function(scope, elem, attrs) {
                scope.run = function(activity, e) {
                    e.stopPropagation();
                    activityService.start(activity, {data: scope.data}).then(function() {
                        if (typeof scope.done === 'function') {
                            scope.done(scope.data);
                        }
                    });
                };
            }
        };
    }];
});
