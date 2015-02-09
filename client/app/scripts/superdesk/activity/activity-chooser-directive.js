define([
    'lodash',
    'require'
], function(_, require) {
    'use strict';

    return ['activityChooser', 'keyboardManager', 'asset', function(activityChooser, keyboardManager, asset) {
        return {
            scope: {},
            templateUrl: asset.templateUrl('superdesk/activity/views/activity-chooser.html'),
            link: function(scope, elem, attrs) {
                var UP = -1,
                    DOWN = 1;

                scope.chooser = activityChooser;
                scope.selected = null;

                function move(diff, items) {
                    var index = _.indexOf(items, scope.selected),
                        next = _.max([0, _.min([items.length - 1, index + diff])]);
                    scope.selected = items[next];
                }

                scope.$watch(function watchActivities() {
                    return activityChooser.activities;
                }, function(activities, prev) {
                    scope.selected = activities ? _.first(activities) : null;

                    if (activities) {
                        keyboardManager.push('up', function() {
                            move(UP, activities);
                        });

                        keyboardManager.push('down', function() {
                            move(DOWN, activities);
                        });

                        keyboardManager.push('enter', function() {
                            activityChooser.resolve(scope.selected);
                        });
                    } else if (prev) {
                        keyboardManager.pop('up');
                        keyboardManager.pop('down');
                        keyboardManager.pop('enter');
                    }
                });

                scope.select = function(activity) {
                    scope.selected = activity;
                };
            }
        };
    }];
});
