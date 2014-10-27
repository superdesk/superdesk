define(['angular', 'jquery'], function(angular, $) {
    'use strict';

    var module = angular.module('superdesk.services.beta', ['superdesk.services.preferencesService']);

    /**
     * Superdesk service for enabling/disabling beta preview in app
     */
    module.service('betaService', ['$window', '$rootScope', 'preferencesService', 'notify',
        function($window, $rootScope, preferencesService, notify) {

        $rootScope.beta = null;

        this.load = function() {
            if (!$rootScope.beta)
            {
                $rootScope.beta = false;
                var beta = preferencesService.get('feature:preview');
                if (beta){
                    $rootScope.beta = beta.enabled;
                }
            }
        };

        this.toggleBeta = function() {
            var update = {
                'feature:preview': {
                    'default':false,
                    'enabled':!$rootScope.beta,
                    'label':'Enable Feature Preview',
                    'type':'bool',
                    'category':'feature'
                }
            };

            preferencesService.update(update, 'feature:preview').then(function() {
                    $rootScope.beta = !$rootScope.beta;
                    $window.location.reload();
                }, function(response) {
                    notify.error(gettext('User preference could not be saved...'));
            });
        };

        this.isBeta = function() {
            this.load();
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
