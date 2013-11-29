define(function() {
    'use strict';

    return ['$compile', function($compile) {
        return {
            restrict: 'A',
            terminal : true,
            scope: { val: '='},
            link: function(scope, element, attrs) {
                var template = '';

                if (scope.val._childOf !== undefined ) {
                    template += '<div class="leaf">'+
                                    '<span class="collapse" ng-click="collapsed = !collapsed">'+
                                        '<i class="icon-chevron-down" ng-show="collapsed"></i>'+
                                        '<i class="icon-chevron-right" ng-show="!collapsed"></i>'+
                                    '</span>'+
                                    '{{val.name}}'+
                                '</div>';
                    template += '<ul class="indent" ng-show="collapsed">'+
                                    '<li>'+
                                        '<div sd-roles-treeview val="val._childOf"></div>'+
                                    '</li>'+
                                '</ul>';
                }
                else {
                    template += '<div class="leaf">{{val.name}}</div>';
                }
                var newElement = angular.element(template);
                $compile(newElement)(scope);
                element.replaceWith(newElement);
            }
        };
    }];
});
