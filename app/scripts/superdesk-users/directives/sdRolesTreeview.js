define(function() {
    'use strict';

    return ['$compile', function($compile) {
        return {
            restrict: 'A',
            terminal : true,
            scope :{ role : '=', roles : '='},
            link: function(scope, element, attrs) {

                if (scope.role.child_of !== undefined ) {
                    scope.childrole = scope.roles[_.findKey(scope.roles, {_id:scope.role.child_of})];
                    scope.treeTemplate = 'scripts/superdesk-users/views/rolesTree.html';
                }
                else {
                    scope.treeTemplate = 'scripts/superdesk-users/views/rolesLeaf.html';
                }

                var template = '<div class="role-holder" ng-include="treeTemplate"></div>';

                var newElement = angular.element(template);
                $compile(newElement)(scope);
                element.replaceWith(newElement);
            }
        };
    }];
});
