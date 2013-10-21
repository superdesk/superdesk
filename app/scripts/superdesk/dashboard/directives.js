define([
    'jquery',
    'angular',
], function($, angular) {
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
         * <div sd-add-widget-box></div>
         * 
         */
        directive('sdAddWidgetBox', function() {
            return {
                templateUrl : 'scripts/superdesk/dashboard/views/addWidgetBox.html',
                restrict: 'A',
                replace: true,
                link : function($scope) {

                    $scope.widgetBoxList = true;
                    $scope.detailsView = null;

                    $scope.showWidgetBox = false;
                    $scope.widgetBoxList = true;

                    $scope.openWidgetBox = function() {
                        $scope.showWidgetBox = true;
                        $scope.widgetBoxList = true;
                    };

                    $scope.closeWidgetBox = function() {
                        $scope.showWidgetBox = !$scope.showWidgetBox;
                    };

                    $scope.viewDetail = function(widget) {
                        $scope.widgetBoxList = false;
                        $scope.detailsView = widget;
                    };

                    $scope.goBack = function() {
                        $scope.widgetBoxList = true;
                    };

                    $scope.selectWidget  = function() {
                        $scope.addWidget($scope.detailsView);
                        $scope.goBack();
                    };
                }
            };
        }).
        /**
         * sdDashboard manager is directive which add functionality of dashboard. It is possible
         * to add, remove, move, edit, resize widgets within dashboard. It is working with gridster.js
         * library to enable all of this.
         *
         * Usage:
         * <div sd-dashboard-manager class="gridster" ng-class="{'editmode': editmode}">
         * 
         */
        directive('sdDashboardManager', function($timeout) {
            return {
                restrict: 'A',
                templateUrl: 'scripts/superdesk/dashboard/views/grid.html',
                link : function($scope, $element) {
                   
                    var ul = $element.find('ul');

                    var defaultOptions = {
                        widget_margins: [20, 20],
                        widget_base_dimensions: [320, 250]
                    };

                    $timeout(function() {

                        angular.forEach($scope.widgets, function(value){
                            value.responsive = responsiveClass(value.sizex, value.sizey);
                        });
                        

                        $scope.gridster = ul.gridster(defaultOptions).data('gridster');
                    
                        $scope.gridster.options.draggable.stop = function() {
                            angular.forEach(ul.find('> li'), function(item, index) {
                                var li = angular.element(item);
                                if (li.attr('class') === 'preview-holder') { return; }
                                var widget = $scope.widgets[index];
                                widget.row = li.attr('data-row');
                                widget.col = li.attr('data-col');
                            });
                            $scope.$apply();
                        };

                        $scope.gridster.disable();
                        
                    });

                    var responsiveClass = function(x,y) {
                        return 'r'+x+y;
                    };
                    
                    var addWidgetToGridster = function() {
                        var li = ul.find('> li').eq($scope.widgets.length-1);
                        var $w = li.addClass('gs_w').appendTo($scope.gridster.$el);
                        $scope.gridster.$widgets = $scope.gridster.$widgets.add($w);
                        $scope.gridster.register_widget($w).add_faux_rows(1).set_dom_grid_height();
                    };

                    $scope.$watch('widgets.length', function(newValue, oldValue) {
                        if (newValue !== oldValue+1) { return; }
                        $timeout(function() { addWidgetToGridster(); });
                    });

                    $scope.editmode = false;

                    $scope.disableDragging = function() {
                        $scope.gridster.disable();
                        $scope.editmode = false;
                    };

                    $scope.enableDragging = function() {
                        $scope.gridster.enable();
                        $scope.editmode = true;
                    };

                    $scope.removeWidget = function(elindex) {
                        var $w = ul.find('> li').eq(elindex);
                        $scope.widgets.splice(elindex,1);
                        $scope.gridster.remove_widget($w);
                    };

                    $scope.resizeWidget = function(index, direction) {
                        var $w = ul.find('> li').eq(index);
                        var widget = $scope.widgets[index];

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

                        $scope.gridster.resize_widget($w, widget.sizex, widget.sizey );
                    };
                }
            };
        });
        
});
