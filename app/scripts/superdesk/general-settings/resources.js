define([
    'angular'
], function(angular) {
    'use strict';

    angular.module('superdesk.generalSettings.resources', []).
       factory('feedSources', function( $resource) {
            return $resource('scripts/superdesk/general-settings/static-resources/sources.json');
        });
});