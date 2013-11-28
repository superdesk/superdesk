define(function() {
    'use strict';

    return ['$compile', function($compile) {
        return {
            restrict: 'A',
            terminal : true,
            scope: { val: '='},
            link: function(scope, element, attrs) {
                var template = '<div class="leaf">{{val.name}}</div>';
                if (angular.isArray(scope.val.items)) {
                    template += '<ul class="indent"><li ng-repeat="item in val.items"><div sd-roles-treeview val="item"></div></li></ul>';
                }
                var newElement = angular.element(template);
                $compile(newElement)(scope);
                element.replaceWith(newElement);
            }
        };
    }];
});
