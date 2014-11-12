define([
    'lodash',
    'require',
    'angular'
], function(_, require, angular) {
    'use strict';

    return angular.module('superdesk.settings', [])
        .config(['superdeskProvider', function(superdesk) {
            superdesk.activity('/settings', {
                label: gettext('Settings'),
                controller: angular.noop,
                templateUrl: require.toUrl('./views/main.html'),
                category: superdesk.MENU_MAIN,
                priority: 1000
            });
        }])
        .directive('sdSettingsView', ['$route', 'superdesk', function($route, superdesk) {
            return {
                scope: {},
                transclude: true,
                templateUrl: require.toUrl('./views/settings-view.html'),
                link: function(scope, elem, attrs) {
                    superdesk.getMenu(superdesk.MENU_SETTINGS).then(function(menu) {
                        scope.settings = menu;
                    });

                    scope.currentRoute = $route.current;
                }
            };
        }])
        .directive('sdValidError', function() {
            return {
                link: function (scope, element) {
                    element.addClass('validation-error');
                }
            };
        })
        .directive('sdRoleUnique', ['api', '$q', function(api, $q) {
            return {
                require: 'ngModel',
                scope: {},
                link: function (scope, element, attrs, ctrl) {

                    /**
                     * Test if given value is unique for seleted field
                     */
                    function testUnique(modelValue, viewValue) {
                        var value = modelValue || viewValue;
                        if (value && attrs.uniqueField) {
                            var criteria = {where: {}};
                            criteria.where[attrs.uniqueField] = value;
                            return api.roles.query(criteria)
                                .then(function(roles) {
                                    if (roles._items.length) {
                                        return $q.reject(roles);
                                    }
                                    return roles;
                                });
                        }

                        // mark as ok
                        return $q.when();
                    }

                    ctrl.$asyncValidators.unique = testUnique;
                }
            };
        }]);
});
