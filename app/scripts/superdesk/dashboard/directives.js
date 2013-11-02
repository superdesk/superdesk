define([
    'jquery',
    'angular'
], function($, angular) {
    'use strict';

    angular.module('superdesk.dashboard.directives', [])
        /**
         * sdWidget give appropriate template to data assgined to it
         *
         * Usage:
         * <div sd-widget data-options="widget" data-definition="widgetDefinition"></div>
         * 
         * Params:
         * @param {Object} options - options for current widget instance
         * @param {Object} definition - definition of widget
         */
        .directive('sdWidget', [function() {
            return {
                templateUrl: 'scripts/superdesk/dashboard/views/widget.html',
                restrict: 'A',
                replace: true,
                scope: {
                    widget: '=',
                }
            };
        }])
        /**
         * sdGrid is directive which add functionality of dashboard. It is possible
         * to add, remove, move, edit, resize widgets within dashboard. It is working with gridster.js
         * library to enable all of this.
         *
         * Usage:
         * <div sd-grid
         *  class="gridster"
         *  ng-class="{'editmode': editmode}"
         *  data-status="widgetBoxStatus"
         *  data-widgets="widgets"></div>
         * 
         * Params:
         * @param {Boolean} status - on/off switch for widget
         * @param {Object} widgets
         */
        .directive('sdGrid', function() {
            return {
                scope: {
                    status: '=',
                    widgets: '='
                },
                replace: true,
                templateUrl: 'scripts/superdesk/dashboard/views/grid.html',
                link: function(scope, element, attrs) {

                    scope.syncWidgets = function() {
                        angular.forEach(scope.widgets, function(widget) {
                            var sizes = scope.gridster.serialize($(widget.el));
                            angular.extend(widget, {
                                row: sizes[0].row,
                                col: sizes[0].col,
                                sizex: sizes[0].size_x,
                                sizey: sizes[0].size_y
                            });
                        });
                    };

                    var root = element.find('ul');
                    scope.gridster = root.gridster({
                        widget_margins: [20, 20],
                        widget_base_dimensions: [320, 250],
                        min_rows: 3,
                        draggable: {
                            stop: function(e, ui, $widget) {
                                scope.syncWidgets();
                            }
                        }
                    }).data('gridster');

                    scope.$watch('status', function(status) {
                        if (scope.gridster) {
                            if (status === true) {
                                scope.gridster.enable();
                            } else {
                                scope.gridster.disable();
                            }
                        }
                    });
                }
            };
        })
        /**
         * sdGridItem is a widget wrapper. Adds resize/remove buttons.
         */
        .directive('sdGridItem', function() {
            return {
                transclude: true,
                templateUrl: 'scripts/superdesk/dashboard/views/grid-item.html',
                link: function(scope, element, attrs) {
                    scope.widget.el = scope.gridster.add_widget(
                        $(element),
                        scope.widget.sizex,
                        scope.widget.sizey,
                        scope.widget.col,
                        scope.widget.row
                    );

                    scope.removeWidget = function(widget) {
                        scope.gridster.remove_widget(widget.el);
                        delete scope.widgets[widget.wcode];
                    };

                    scope.resizeWidget = function(widget, direction) {
                        switch(direction) {
                        case 'left':
                            if (widget.sizex !== 1) {
                                widget.sizex--;
                            }
                            break;
                        case 'right':
                            if (widget.sizex !== widget.max_sizex) {
                                widget.sizex++;
                            }
                            break;
                        case 'up':
                            if (widget.sizey !== 1) {
                                widget.sizey--;
                            }
                            break;
                        case 'down':
                            if (widget.sizey !== widget.max_sizey) {
                                widget.sizey++;
                            }
                            break;
                        }

                        scope.gridster.resize_widget($(element), widget.sizex, widget.sizey);
                        scope.syncWidgets();
                    };
                }
            };
        });
});
