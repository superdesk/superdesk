define(['angular', 'jquery'], function(angular, $) {
    'use strict';

    var module = angular.module('superdesk.services.beta', []);

    /**
     * Superdesk service for enabling/disabling beta preview in app
     */
    module.service('betaService', ['$window', '$rootScope',
        function($window, $rootScope) {

        $rootScope.beta = localStorage.getItem('beta') === 'true';

        this.toggleBeta = function() {
            $rootScope.beta = !$rootScope.beta;
            localStorage.setItem('beta', $rootScope.beta);
            $window.location.reload();
        };

        this.isBeta = function() {
			return $rootScope.beta;
        };
    }]);

    module.config(['$httpProvider', function($httpProvider) {
        $httpProvider.interceptors.push(BetaTemplateInterceptor);
    }]);

    /**
     * Detect beta elements in phase of loading html templates and prevent rendering of those
     */
    BetaTemplateInterceptor.$inject = ['$q', '$templateCache', 'betaService'];
    function BetaTemplateInterceptor($q, $templateCache, betaService) {
        var modifiedTemplates = {};

        var HAS_FLAGS_EXP = /sd-beta/,
            IS_HTML_PAGE = /\.html$|\.html\?/i;

        return {
            response: function(response) {
                var url = response.config.url;

                if (!modifiedTemplates[url] && IS_HTML_PAGE.test(url) && HAS_FLAGS_EXP.test(response.data)) {
                    var template = $('<div>').append(response.data);

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
            }
        };
    }

    return module;
});
