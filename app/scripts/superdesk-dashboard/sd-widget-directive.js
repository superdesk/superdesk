define([
    'require',
    './configuration-controller'
], function(require) {
    'use strict';

    /**
     * sdWidget give appropriate template to data assgined to it
     *
     * Usage:
     * <div sd-widget data-widget="widget"></div>
     *
     * Params:
     * @scope {Object} widget
     */
    return ['$modal', function($modal) {
        return {
            templateUrl: require.toUrl('./views/widget.html'),
            restrict: 'A',
            replace: true,
            transclude: true,
            scope: {widget: '='},
            link: function(scope, element, attrs) {
                scope.openConfiguration = function() {
                    $modal.open({
                        templateUrl: require.toUrl('./views/configuration.html'),
                        controller: require('./configuration-controller'),
                        scope: scope
                    });
                };
            }
        };
    }];
});
