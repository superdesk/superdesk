define(['angular'], function (angular) {
    'use strict';

    return angular.module('superdesk.slider.directives', []).
        /**
         * Slider directive
         *
         * Usage:
         *  <div sd-slider data-value="urgency" data-list="newsvalue" data-unique="value" data-invert="true" data-update="update(item)">
         *  </div>
         *
         * Params:
         * @scope {Object} value - current selected value, if nothing is selected it will use min value
         * @scope {Object} list - list of options
         * @scope {Boolen} disabled - disable or enable slider functionality
         * @scope {Object} invert - inverts min and max value
         * @scope {Function} update - callback when slider value is changed
         *
         */
        directive('sdSlider', function () {
            return {
                transclude: true,
                templateUrl: 'scripts/superdesk/views/sdSlider.html',
                scope: {
                    value: '=',
                    list: '=',
                    unique: '@',
                    field: '@',
                    disabled: '=',
                    invert: '=',
                    update: '&'
                },
                link: function (scope, element, attrs, controller) {
                    scope.$watch('list', function (list) {
                        if (!list) {
                            return false;
                        }

                        var value = scope.invert ?
                                -Math.abs(parseInt(scope.value)) :
                                parseInt(scope.value),

                            minValue = scope.invert ?
                                -Math.abs(parseInt(scope.list[scope.list.length - 1][scope.unique])) :
                                parseInt(scope.list[0][scope.unique]),

                            maxValue = scope.invert ?
                                -Math.abs(parseInt(scope.list[0][scope.unique])) :
                                parseInt(scope.list[scope.list.length - 1][scope.unique]);

                        if (!value) {
                            value = minValue;
                        }

                        $('[sd-slider]').slider({
                            range: 'max',
                            min: minValue,
                            max: maxValue,
                            value: value,
                            disabled: scope.disabled,
                            create: function () {
                                $(this).find('.ui-slider-thumb')
                                        .css('left', ((value - minValue) * 100) / (maxValue - minValue) + '%')
                                        .text(scope.invert ? Math.abs(value) : value);
                            },
                            slide: function (event, ui) {
                                $(this).find('.ui-slider-thumb')
                                        .css('left', ((ui.value - minValue) * 100) / (maxValue - minValue) + '%')
                                        .text(scope.invert ? Math.abs(ui.value) : ui.value);

                                scope.update({
                                    item: scope.invert ? scope.list[Math.abs(ui.value) - 1] : scope.list[ui.value] - 1,
                                    field: scope.field
                                });
                            },
                            start: function () {
                                $(this).find('.ui-slider-thumb').addClass('ui-slider-thumb-active');
                            },
                            stop: function () {
                                $(this).find('.ui-slider-thumb').removeClass('ui-slider-thumb-active');
                            }
                        });

                    });
                }
            };
        });
});
