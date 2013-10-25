define([
    'angular'
], function(angular) {
    'use strict';

    angular.module('superdesk.generalSettings.directives', [])
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
            templateUrl : 'scripts/superdesk/general-settings/views/settings-module.html',
            restrict : 'A',
            replace : true,
            transclude: true,
            scope : {
                title : '='
            },
            link : function(scope,element,attrs) {

                scope.visible = true;

                scope.toggle= function() {
                    scope.visible = !scope.visible;
                };
            }
        };
    })
    /**
     * sdSourceInfo displays  info about source (last update time)
     *
     * Usage:
     * <div sd-source-info title="someTitle">
     * 
     * Params:
     * @param {Object} source - object representing source
     *
     */
    .directive('sdSourceInfo', function($compile){
        return {
            restrict : 'A',
            scope : {
                source : '='
            },
            link : function(scope,element,attrs) {
                var el = $compile('<div class="last-updated"><span trnaslate>Last updated</span>{{source.lastUpdated}}</div>')(scope);
                element.find('> header').append(el);
            }
        };
    });
        
});