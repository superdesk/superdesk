define([
    'require'
], function(require) {
    'use strict';

    return ['activityService', 'asset', function(activityService, asset) {
        return {
            scope: true,
            templateUrl: asset.templateUrl('superdesk/activity/views/activity-modal.html'),
            link: function(scope, elem) {
                scope.stack = activityService.activityStack;
                scope.$watch('stack.length', function(len) {
                    scope.activity = null;
                    if (len) {
                        var config = scope.stack[len - 1];
                        scope.activity = config.activity;
                        scope.locals = config.locals;

                        scope.reject = function(reason) {
                            return config.defer.reject(reason);
                        };

                        scope.resolve = function(result) {
                            return config.defer.resolve(result);
                        };

                        config.defer.promise['finally'](function() {
                            scope.stack.pop();
                        });
                    }
                });
            }
        };
    }];
});
