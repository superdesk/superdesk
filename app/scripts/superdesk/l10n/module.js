define(['angular'], function(angular) {
    'use strict';

    angular.module('superdesk.l10n', []).
        service('translate', [function() {
            var translations = null;

            /**
             * Load translations
             */
            function loadTranslations() {
                if (translations === null) {
                    translations = {};
                }
            }

            return {
                /**
                 * Provides a wrapper for translations
                 */
                _: function(args) {
                    loadTranslations();

                    if (!arguments.length) {
                        return;
                    }

                    var key = arguments[0];
                    return key in translations ? translations[key] : key;
                }
            };
        }]).
        run(['$rootScope', 'translate', function($rootScope, translate) {
            $rootScope._ = function() {
                return translate._.apply(translate, arguments);
            };
        }]);
});