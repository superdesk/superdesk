define([
    'jquery',
    'angular',
], function($, angular) {
    'use strict';

    angular.module('superdesk.dashboard.directives', []).
        factory('widgetList', function( $resource) {
            return $resource('scripts/superdesk/dashboard/static-resources/widgets.json');
        }).
        directive('sdWidget', function() {
            return {
                templateUrl : 'scripts/superdesk/dashboard/views/widget.html',
                restrict: 'A',
                replace: true,
                scope: {
                    widget : "="
                }
            };
        }).
        filter('isWcode', function() {
          return function(input, values) {
            var out = [];
              for (var i = 0; i < input.length; i++){
                for (var j=0; j < values.length; j++)
                  if(input[i].wcode == values[j])
                      out.push(input[i]);
              }      
            return out;
          };
        }).
        directive('dashboardManager', function($timeout) {
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

                        angular.forEach($scope.widgets, function(value, key){
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
                    }
                    

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
                                (widget.sizex == widget.max_sizex) ? '' : widget.sizex++;
                                break;
                            case "up" : 
                                widget.sizey == 1 ?  '' : widget.sizey--;
                                break;
                            case "down" :
                                (widget.sizey == widget.max_sizey) ? '' : widget.sizey++;
                                break;
                        }

                        widget.responsive = responsiveClass(widget.sizex,widget.sizey);

                        $scope.gridster.resize_widget($w, widget.sizex, widget.sizey )
                    };
                }
            };
        }).
        directive('sdAddWidgetBox', function(widgetList, $timeout) {
            return {
                templateUrl : 'scripts/superdesk/dashboard/views/addWidgetBox.html',
                restrict: 'A',
                replace: true,
                link : function($scope, $element, $attrs) {

                    $scope.widgetBoxList = true;
                    $scope.detailsView = null;




                    $scope.viewDetail = function(index) {
                         $scope.widgetBoxList = false;
                         $scope.detailsView = $scope.allWidgets[index];
                    }

                    $scope.goBack = function() {
                         $scope.widgetBoxList = true;
                    }

                    $scope.selectWidget  = function() {
                        $scope.addWidget($scope.detailsView);
                        $scope.goBack();
                    }
                                    }
            }
        });
        
});