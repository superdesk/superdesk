define(function() {
    'use strict';

    return ['$compile', function($compile) {
        return {
            restrict: 'A',
            terminal : true,
            scope: {role: '='},
            link: function(scope, element, attrs) {
                var template = '';

                if (scope.role.child_of !== undefined ) {
                    template += '<div class="leaf">'+
                                    '<span class="collapse" ng-click="collapsed = !collapsed">'+
                                        '<i class="icon-chevron-down" ng-show="collapsed"></i>'+
                                        '<i class="icon-chevron-right" ng-show="!collapsed"></i>'+
                                    '</span>'+
                                    '{{role.name}}'+
                                '</div>';
                    template += '<ul class="indent" ng-show="collapsed">'+
                                    '<li>'+
                                        '<div sd-roles-treeview data-role="role.child_of"></div>'+
                                    '</li>'+
                                '</ul>';
                }
                else {
                    template += '<div class="leaf">{{role.name}}</div>';
                }
                var newElement = angular.element(template);
                $compile(newElement)(scope);
                element.replaceWith(newElement);
            }
        };
    }];
});
