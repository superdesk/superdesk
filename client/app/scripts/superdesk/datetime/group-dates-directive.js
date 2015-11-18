define(['moment'], function(moment) {
    'use strict';

    /**
     * sdGroupDates directive will group list items by a date provided as a param.
     *
     * Usage:
     * <li ng-repeat="item in items" ng-model="item" sd-group-dates="updated">
     *
     * Params:
     * @scope {object} ngModel
     * @scope {string} sdGroupDates - model field to group by
     */
    return function() {
        var lastDate = null;
        var COMPARE_FORMAT = 'YYYY-M-D';
        var DISPLAY_DATE_FORMAT = 'D. MMMM YYYY';
        var DISPLAY_CDATE_FORMAT = 'D. MMMM';
        var DISPLAY_DAY_FORMAT = 'dddd, ';
        var DISPLAY_TODAY_FORMAT = '[Today], ';
        return {
            require: 'ngModel',
            link: function(scope, element, attrs, ngModel) {
                ngModel.$render = function() {
                    var date = moment.utc(ngModel.$viewValue[attrs.sdGroupDates]);
                    if (scope.$first || lastDate.format(COMPARE_FORMAT) !== date.format(COMPARE_FORMAT)) {
                        var fdate;
                        var fday;
                        if (moment().format(COMPARE_FORMAT) === date.format(COMPARE_FORMAT)){
                            fday = date.format(DISPLAY_TODAY_FORMAT);
                        } else {
                            fday = date.format(DISPLAY_DAY_FORMAT);
                        }

                        if (moment().format('YYYY') === date.format('YYYY')){
                            fdate = date.format(DISPLAY_CDATE_FORMAT);
                        } else {
                            fdate = date.format(DISPLAY_DATE_FORMAT);
                        }
                        element.prepend('<div class="date"><span>' + fday + fdate + '</span></div>');
                        element.addClass('with-date');
                        lastDate = date;
                    }
                };
            }
        };
    };
});
