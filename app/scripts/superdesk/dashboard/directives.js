define([
    'angular',
], function(angular) {
    'use strict';

    angular.module('superdesk.dashboard.directives', []).
        /**
         * sdWidget give appropriate template to data assgined to it
         *
         * Usage:
         * <div sd-widget widget="someWidget"></div>
         * 
         * Params:
         * @param {object} widget - object with predefined structure fileds
         */
        directive('sdWidget', function() {
            return {
                templateUrl : 'scripts/superdesk/dashboard/views/widget.html',
                restrict: 'A',
                replace: true,
                scope: {
                    widget : '='
                }
            };
        }).
        /**
         * sdWAddWidgetBox is modal window for adding new widget to dashboard
         *
         * Usage:
         * <div sd-add-widget-box sd-status="widgetBoxStatus" data-model="widgets"></div>
         * 
         * Params:
         * @param {Boolean} status - on/off switch for widget
         * @param {Object} dataModel - model for data
         */
        directive('sdAddWidgetBox', ['widgetService', function(widgetService) {
            return {
                templateUrl: 'scripts/superdesk/dashboard/views/addWidgetBox.html',
                scope: {
                    status: '=sdStatus',
                    model: '=model'
                },
                replace: true,
                link: function(scope, element, attrs) {
                    scope.addWidget = function(widget) {
                        widget.row = 1;
                        widget.col = 1;
                        
                        scope.model.push(widget);
                        widgetService.saveWidgets(scope.model);

                        //if (!$scope.editmode)  {$scope.enableDragging();}
                    };

                    scope.widgetList = widgetService.getWidgetList();
                }
            };
        }]).
        /**
         * sdDashboard manager is directive which add functionality of dashboard. It is possible
         * to add, remove, move, edit, resize widgets within dashboard. It is working with gridster.js
         * library to enable all of this.
         *
         * Usage:
         * <div sd-dashboard-manager
         *  class="gridster"
         *  ng-class="{'editmode': editmode}"
         *  sd-status="widgetBoxStatus"
         *  data-model="widgets"></div>
         * 
         * Params:
         * @param {Boolean} status - on/off switch for widget
         * @param {Object} dataModel - model for data
         */
        directive('sdDashboardManager', ['$timeout', 'widgetService', function($timeout, widgetService) {
            var defaultOptions = {
                widget_margins: [20, 20],
                widget_base_dimensions: [320, 250]
            };

            var responsiveClass = function(x, y) {
                return 'r' + x + y;
            };

            return {
                restrict: 'A',
                scope: {
                    status: '=sdStatus',
                    model: '=model'
                },
                templateUrl: 'scripts/superdesk/dashboard/views/grid.html',
                link : function(scope, element, attrs) {
                    var ul = element.find('ul');

                    scope.$watch('status', function(status) {
                        if (scope.gridster) {
                            if (status === true) {
                                scope.gridster.enable();
                            } else {
                                scope.gridster.disable();
                            }
                        }
                    });

                    $timeout(function() {
                        angular.forEach(scope.model, function(value){
                            value.responsive = responsiveClass(value.sizex, value.sizey);
                        });
                        scope.gridster = ul.gridster(defaultOptions).data('gridster');
                        scope.gridster.disable();
                        scope.gridster.options.draggable.stop = function() {
                            angular.forEach(ul.find('> li'), function(item, index) {
                                var li = angular.element(item);
                                if (li.attr('class') === 'preview-holder') { return; }
                                var widget = scope.model[index];
                                widget.row = li.attr('data-row');
                                widget.col = li.attr('data-col');
                            });
                            scope.$apply();
                        };
                    });

                    scope.$watch('model.length', function(newValue, oldValue) {
                        if (newValue !== oldValue+1) { return; }
                        $timeout(function() { addWidgetToGridster(); });
                    });
                    
                    var addWidgetToGridster = function() {
                        var li = ul.find('> li').eq(scope.model.length-1);
                        var w = li.addClass('gs_w').appendTo(scope.gridster.$el);
                        scope.gridster.$widgets = scope.gridster.$widgets.add(w);
                        scope.gridster.register_widget(w).add_faux_rows(1).set_dom_grid_height();
                    };

                    scope.removeWidget = function(elindex) {
                        var w = ul.find('> li').eq(elindex);
                        scope.model.splice(elindex,1);
                        scope.gridster.remove_widget(w);
                    };

                    scope.resizeWidget = function(index, direction) {
                        var w = ul.find('> li').eq(index);
                        var widget = scope.model[index];

                        switch(direction) {
                        case 'left' :
                            if (widget.sizex !== 1) {
                                widget.sizex--;
                            }
                            break;
                        case 'right' :
                            if (widget.sizex !== widget.max_sizex) {
                                widget.sizex++;
                            }
                            break;
                        case 'up' :
                            if (widget.sizey !== 1) {
                                widget.sizey--;
                            }
                            break;
                        case 'down' :
                            if (widget.sizey !== widget.max_sizey) {
                                widget.sizey++;
                            }
                            break;
                        }

                        widget.responsive = responsiveClass(widget.sizex,widget.sizey);

                        scope.gridster.resize_widget(w, widget.sizex, widget.sizey );
                    };
                }
            };
        }]);
        
});
