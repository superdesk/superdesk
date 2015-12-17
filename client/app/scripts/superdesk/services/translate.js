(function() {
    'use strict';

    /**
     * Translate module
     *
     * This module provides localization support.
     * It's using angular-gettext.
     */
    return angular.module('superdesk.translate', ['gettext'])
        .run(['gettextCatalog', '$location', '$rootScope', 'SESSION_EVENTS',
            function(gettextCatalog, $location, $rootScope, SESSION_EVENTS) {

                $rootScope.$on(SESSION_EVENTS.IDENTITY_LOADED, function(event) {
                    if ($rootScope.$root.currentUser && gettextCatalog.strings.hasOwnProperty($rootScope.$root.currentUser.language)) {
                        //if the current logged in user has a saved language preference that is available
                        gettextCatalog.setCurrentLanguage($rootScope.$root.currentUser.language);
                    } else {
                        if (gettextCatalog.strings.hasOwnProperty(window.navigator.language)) {
                            //no saved preference but browser language is available
                            gettextCatalog.setCurrentLanguage(window.navigator.language);
                        } else {
                            //no other options available go with baseLanguage
                            gettextCatalog.setCurrentLanguage(gettextCatalog.baseLanguage);
                        }
                    }
                });
                var params = $location.search();
                if ('lang' in params) {
                    gettextCatalog.currentLanguage = params.lang;
                    gettextCatalog.debug = true;
                }
            }])
        /**
         * Gettext service to be used in controllers/services/directives.
         *
         * Usage:
         * function($scope, gettext) { $scope.translatedMessage = gettext("Translate Me"); }
         *
         * This way "Translate Me" can be found by the string extractor and it will return
         * translated string if appropriet.
         */
        .factory('gettext', ['gettextCatalog', function(gettextCatalog) {
            return function(input) {
                return gettextCatalog.getString(input);
            };
        }]);
})();
