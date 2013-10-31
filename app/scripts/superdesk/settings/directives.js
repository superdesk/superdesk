define([
    'angular'
], function(angular) {
    'use strict';

    angular.module('superdesk.settings.directives', [])
     /**
     * sdSettingsModule creates a toggle settings box
     *
     * Usage:
     * <div sd-settings-module title="someTitle">
     * 
     * Params:
     * @param {String} title - title for the module
     *
     */
    .directive('sdSettingsModule', function(){
        return {
            templateUrl : 'scripts/superdesk/settings/views/settings-module.html',
            restrict : 'A',
            replace : true,
            transclude: true,
            link : function(scope,element,attrs) {
                scope.visible = true;
                scope.toggle= function() {
                    scope.visible = !scope.visible;
                };
            }
        };
    });
});