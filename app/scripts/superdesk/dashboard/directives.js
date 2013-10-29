define([
    'angular',
], function(angular) {
    'use strict';

    angular.module('superdesk.dashboard.directives', [])
        /**
         * sdWidget give appropriate template to data assgined to it
         *
         * Usage:
         * <div sd-widget wcode="someWidget" sd-widget-list="widgetList"></div>
         * 
         * Params:
         * @param {string} wcode - wcode of widget
         * @param {Object} widgetList - widgetList
         */
        .directive('sdWidget', [function() {
            return {
                templateUrl : 'scripts/superdesk/dashboard/views/widget.html',
                restrict: 'A',
                scope: {
                    wcode: '=sdWcode',
                    widgetList: '=sdWidgetList'
                },
                replace: true,
                link: function(scope, element, attrs) {
                    
                }
            };
        }])
        /**
         * sdGridster is directive which add functionality of dashboard. It is possible
         * to add, remove, move, edit, resize widgets within dashboard. It is working with gridster.js
         * library to enable all of this.
         *
         * Usage:
         * <div sd-gridster
         *  class="gridster"
         *  ng-class="{'editmode': editmode}"
         *  sd-status="widgetBoxStatus"
         *  data-model="widgets"></div>
         *  sd-widget-list="widgetList"></div>
         * 
         * Params:
         * @param {Boolean} status - on/off switch for widget
         * @param {Object} dataModel - model for data
         * @param {Object} widgetList - widgetList
         */
        .directive('sdGridster', ['$timeout', function($timeout) {
            
            var defaultOptions = {
                widget_margins: [20, 20],
                widget_base_dimensions: [320, 250],
                min_rows: 3
            };

            return {
                scope: {
                    status: '=sdStatus',
                    widgetList: '=sdWidgetList',
                    model: '=model'
                },
                replace: true,
                templateUrl: 'scripts/superdesk/dashboard/views/grid.html',
                link: function(scope, element, attrs) {
                    scope.resizeWidget = function(wcode, direction) {
                        var widget = scope.model[wcode];
                        switch(direction) {
                        case 'left':
                            if (widget.sizex !== 1) {
                                widget.sizex--;
                            }
                            break;
                        case 'right':
                            if (widget.sizex !== scope.widgetList[wcode].max_sizex) {
                                widget.sizex++;
                            }
                            break;
                        case 'up':
                            if (widget.sizey !== 1) {
                                widget.sizey--;
                            }
                            break;
                        case 'down':
                            if (widget.sizey !== scope.widgetList[wcode].max_sizey) {
                                widget.sizey++;
                            }
                            break;
                        }
                    };
                    scope.removeWidget = function(wcode) {
                        delete scope.model[wcode];
                    };
                    scope.update = function() {
                        $timeout(function() {
                            _.forEach(root.find('> li'), function(item, index) {
                                var li = angular.element(item);
                                if (li.attr('class') === 'preview-holder') { return; }
                                var wcode = li.data('widget');
                                var widget = scope.model[wcode];
                                widget.row = parseInt(li.attr('data-row'), 10) || 1;
                                widget.col = parseInt(li.attr('data-col'), 10) || 1;
                                scope.gridster.register_widget($(li));
                                scope.gridster.resize_widget($(li), widget.sizex, widget.sizey);
                            });
                            scope.gridster.generate_grid_and_stylesheet();
                        });
                    };

                    //
                    var root = element.find('ul');

                    scope.gridster = root.gridster(defaultOptions)
                        .data('gridster');

                    scope.$watch('status', function(status) {
                        if (scope.gridster) {
                            if (status === true) {
                                scope.gridster.enable();
                            } else {
                                scope.gridster.disable();
                            }
                        }
                    });
                    scope.$watch('model', function(model, oldModel) {
                        scope.update();
                    }, true);
                }
            };
        }])
});
