define([
    'jquery',
    'angular',
    'bootstrap_ui'
], function($, angular, bootstrap_ui) {
    'use strict';

    angular.module('superdesk.dashboard.directives', []).
        directive('sdWidget', function() {
            return {
                templateUrl : 'scripts/superdesk/dashboard/views/widget.html',
                replace: true,
                transclude: true,
                restrict: 'A',
                require : 'ngModel'
            };
        }).
        directive('gridster', function($timeout) {
            return {
                restrict: 'A',
                require : 'ngModel',
                template: '<ul><div sd-grid-widget ng-repeat="widget in widgets" ng-model="widget"></div></ul>',
                link: function($scope, $element, $attributes, $controller) {
                    
                    var gridster;
                    var ul = $element.find('ul');

                    var defaultOptions = {
                        widget_margins: [20, 20],
                        widget_base_dimensions: [320, 250]
                    };

                    $timeout(function() {
                        gridster = ul.gridster(defaultOptions).data('gridster');
                    
                        gridster.options.draggable.stop = function(event, ui) {
                            angular.forEach(ul.find('> li'), function(item, index) {
                                var li = angular.element(item);
                                if (li.attr('class') === 'preview-holder') return;
                                var widget = $scope.widgets[index];
                                widget.row = li.attr('data-row');
                                widget.col = li.attr('data-col');
                            });
                            $scope.$apply();
                        };
                    });                    
                }
            };
        }).
        
        directive('sdGridWidget', function() {
            return {
                restrict: 'AC',
                require : 'ngModel',
                replace: true,
                template:
                    '<li data-col="{{widget.col}}" data-row="{{widget.row}}" data-sizex="{{widget.sizex}}" data-sizey="{{widget.sizey}}">'+
                        '<div sd-widget ng-model="widget"></div>'+
                    '</li>',
                link: function($scope, $element, $attributes, $controller) {
                }
            };
        })
        
});