define([
    'jquery',
    'angular',
], function($, angular) {
    'use strict';

    angular.module('superdesk.dashboard.directives', []).
        directive('sdWidget', function() {
            return {
                templateUrl : 'scripts/superdesk/dashboard/views/widget.html',
                replace: true,
                transclude: true,
                restrict: 'A'
            };
        }).
        directive('dashboardManager', function($timeout) {
            return {
                restrict: 'A',
                template: '<ul class="dash-grid"><div sd-grid-widget ng-repeat="widget in widgets" ng-model="widget"></div></ul>',
                controller : function($scope, $element) {
                   
                    var ul = $element.find('ul');

                    var defaultOptions = {
                        widget_margins: [20, 20],
                        widget_base_dimensions: [320, 250]
                    };

                    $timeout(function() {
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

                    $scope.removeWidget = function(elindex) {
                        var $w = ul.find('> li').eq(elindex);
                        $scope.widgets.splice(elindex,1);
                        $scope.gridster.remove_widget($w);
                    };

                    $scope.resizeWidget = function(index, direction) {
                        var $w = ul.find('> li').eq(index);
                        var widget = $scope.widgets[index];
                        switch(direction) {
                            case "left" : 
                                widget.sizex == 1 ?  '' : widget.sizex--;
                                break;
                            case "right" :
                                widget.sizex == 4 ? '' : widget.sizex++;
                                break;
                            case "up" : 
                                widget.sizey == 1 ?  '' : widget.sizey--;
                                break;
                            case "down" :
                                widget.sizey++;
                                break;
                        }
                       
                        $scope.gridster.resize_widget($w, widget.sizex, widget.sizey )
                    };
                }
            };
        }).
        
        directive('sdGridWidget', function() {
            return {
                restrict: 'A',
                replace: true,
                template:
                    '<li data-col="{{widget.col}}" data-row="{{widget.row}}" data-sizex="{{widget.sizex}}" data-sizey="{{widget.sizey}}">'+
                        '<div class="widget-resize-width" ng-show="editmode">'+
                            '<div class="resize-left" ng-click="resizeWidget($index,\'left\')" ></div>'+
                            '<div class="resize-right" ng-click="resizeWidget($index,\'right\')" ></div>'+
                        '</div>'+
                        '<div class="widget-resize-height" ng-show="editmode">'+
                            '<div class="resize-up" ng-click="resizeWidget($index,\'up\')" ></div>'+
                            '<div class="resize-down" ng-click="resizeWidget($index,\'down\')" ></div>'+
                        '</div>'+
                        '<div class="widget-close" ng-click="removeWidget($index)" ng-show="editmode"></div>'+
                        '<div sd-widget></div>'+
                    '</li>',
            };
        });
        
});