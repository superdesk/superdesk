define([
    'angular',
    'angular-resource'
], function(angular) {
    'use strict';

    angular.module('superdesk.api', ['ngResource']).
        value('api_url', ServerConfig.url).
        factory('apiUrl', function(api_url) {
            return function(url) {
                return api_url + url;
            };
        }).
        factory('resource', function($resource, apiUrl) {
            function setDefaultActions(actions) {
                var defaultActions = {
                    query: {method: 'GET', isArray: false}
                };

                actions = angular.extend(defaultActions, actions);
            }

            function fixMethodUrls(actions) {
                if (angular.isObject(actions)) {
                    angular.forEach(actions, function(action) {
                        if ('url' in action) {
                            action.url = apiUrl(action.url);
                        }
                    });
                }
            }

            return function(url, paramDefaults, actions) {
                setDefaultActions(actions);
                fixMethodUrls(actions);
                return $resource(apiUrl(url), paramDefaults, actions);
            };
        });
});