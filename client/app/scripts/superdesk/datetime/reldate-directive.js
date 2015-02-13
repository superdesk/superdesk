define(['moment'], function(moment) {
    'use strict';

    /**
     * Display relative date in <time> element
     *
     * Usage:
     * <span sd-reldate ng-model="user._created"></span>
     *
     * Params:
     * @param {object} ngModel - datetime string in utc
     */
    return function() {
        return {
            require: 'ngModel',
            template: '<time datetime="{{ datetime }}" title="{{ title }}">{{ reldate }}</time>',
            replate: true,
            link: function(scope, element, attrs, ngModel) {
                ngModel.$render = function() {
                    var date = moment.utc(ngModel.$viewValue);
                    scope.datetime = date.toISOString();

                    date.local(); // switch to local time zone
                    scope.title = date.format('LLLL');
                    scope.reldate = date.fromNow();
                };
            }
        };
    };
});
