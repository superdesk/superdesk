define(['angular', 'lodash'], function(angular, _) {
    'use strict';

    var module = angular.module('superdesk.services');

    /**
     * Superdesk service for enabling/disabling beta preview in app
     */
    module.service('betaService', ['$window', '$rootScope', 'storage',
        function($window, $rootScope, storage) {

        $rootScope.beta = localStorage.getItem('beta') === 'true';

        this.toggleBeta = function() {
            localStorage.setItem('beta', !$rootScope.beta);
            $window.location.reload();
        };

        this.isBeta = function() {
			return $rootScope.beta;
        };

    }]);

	/**
	* Detect beta elements in phase of loading html templates and prevent rendering of those
	*/
	module.config(['$httpProvider', function($httpProvider) {
        $httpProvider.responseInterceptors.push([
            '$q', '$templateCache', 'betaService',
            function($q, $templateCache, betaService) {

                var modifiedTemplates = {};

                var HAS_FLAGS_EXP = /sd-beta/;

                var IS_HTML_PAGE = /\.html$|\.html\?/i;

                return function(promise) {
                    return promise.then(function(response) {
                        var url = response.config.url,
                        responseData = response.data;

                        if (!modifiedTemplates[url] && IS_HTML_PAGE.test(url) &&
                        HAS_FLAGS_EXP.test(responseData)) {

                            var template = $('<div>').append(responseData);

                            if (!betaService.isBeta()) {
                                template.find('[sd-beta]').each(function() {
                                    $(this).remove();
                                });
                            }

                            response.data = template.html();

                            $templateCache.put(url, response.data);
                            modifiedTemplates[url] = true;
                        }

                        return response;
                    },

                    function(response) {
                        return $q.reject(response);
                    });
                };
            }
        ]);
    }]);
});
