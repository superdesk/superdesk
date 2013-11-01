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
                templateUrl : 'scripts/superdesk/dashboard/views/widget.html',
                restrict: 'A',
                scope: {
                    options: '=options',
                    definition: '=definition'
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
         *  data-status="widgetBoxStatus"
         *  data-model="widgets"></div>
         *  data-widget-list="widgetList"></div>
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
                    status: '=status',
                    widgetList: '=widgetList',
                    model: '=model'
                },
                replace: true,
                templateUrl: 'scripts/superdesk/dashboard/views/grid.html',
                link: function(scope, element, attrs) {
                    scope.resizeWidget = function(widget, direction) {
                        switch(direction) {
                        case 'left':
                            if (widget.sizex !== 1) {
                                widget.sizex--;
                            }
                            break;
                        case 'right':
                            if (widget.sizex !== scope.widgetList[widget.wcode].max_sizex) {
                                widget.sizex++;
                            }
                            break;
                        case 'up':
                            if (widget.sizey !== 1) {
                                widget.sizey--;
                            }
                            break;
                        case 'down':
                            if (widget.sizey !== scope.widgetList[widget.wcode].max_sizey) {
                                widget.sizey++;
                            }
                            break;
                        }
                    };
                    scope.removeWidget = function(widget) {
                        _.forEach(scope.widgets, function(item, index) {
                            if (item.wcode === widget.wcode) {
                                scope.widgets.splice(index, 1);
                            }
                        });
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

                    scope.gridster = root.gridster(defaultOptions).data('gridster');

                    scope.gridster.options.draggable.stop = function(event, ui) {
                        scope.update();
                    };

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
                        var widgets = [];
                        _.forEach(scope.model, function(data, wcode) {
                            widgets.push(_.extend({}, data, {wcode: wcode}));
                        });
                        scope.widgets = widgets;

                        scope.update();
                    }, true);

                    scope.$watch('widgets', function(widgets, oldWidgets) {
                        var model = {};
                        _.forEach(widgets, function(data) {
                            model[data.wcode] = {
                                sizex: data.sizex,
                                sizey: data.sizey,
                                row: data.row,
                                col: data.col
                            };
                        });
                        scope.model = model;
                    }, true);
                }
            };
        }]);
});
