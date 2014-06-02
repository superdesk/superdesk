require.config({
    shim: {
        'bower_components/gridster/dist/jquery.gridster.with-extras': ['jquery']
    }
});

define([
    'jquery',
    'angular',
    'require',
    'bower_components/gridster/dist/jquery.gridster.with-extras'
], function($, angular, require) {
    'use strict';

    angular.module('superdesk.dashboard.grid', [])
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
         * @scope {Boolean} status - on/off switch for widget
         * @scope {Object} widgets
         */
        .directive('sdGrid', function() {
            return {
                scope: {
                    status: '=',
                    widgets: '='
                },
                replace: true,
                templateUrl: require.toUrl('./views/grid.html'),
                controller: ['$scope', function($scope) {
                    this.addWidget = function(element, sizex, sizey, col, row) {
                        return $scope.gridster.add_widget(element, sizex, sizey, col, row);
                    };
                    this.removeWidget = function(id) {
                        $scope.gridster.remove_widget($scope.widgets[id].el);
                        delete $scope.widgets[id];
                    };
                    this.resizeWidget = function(element, sizex, sizey) {
                        $scope.gridster.resize_widget(element, sizex, sizey);
                        $scope.syncWidgets();
                    };
                }],
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
                require: '^sdGrid',
                transclude: true,
                templateUrl: require.toUrl('./views/grid-item.html'),
                link: function(scope, element, attrs, sdGrid) {
                    scope.widget.el = sdGrid.addWidget(
                        $(element),
                        scope.widget.sizex,
                        scope.widget.sizey,
                        scope.widget.col,
                        scope.widget.row
                    );

                    scope.removeWidget = function(widget) {
                        sdGrid.removeWidget(widget);
                    };

                    scope.resizeWidget = function(widget, direction) {
                        switch (direction) {
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

                        sdGrid.resizeWidget($(element), widget.sizex, widget.sizey);
                    };
                }
            };
        });
});
