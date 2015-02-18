/**
 * This file is part of Superdesk.
 *
 * Copyright 2013, 2014 Sourcefabric z.u. and contributors.
 *
 * For the full copyright and license information, please see the
 * AUTHORS and LICENSE files distributed with this source code, or
 * at https://www.sourcefabric.org/superdesk/license
 */

(function() {

    'use strict';

    var app = angular.module('superdesk.docs', []);

    MainDocsView.$inject = ['$location', '$anchorScroll'];
    function MainDocsView($location, $anchorScroll) {
        return {
            templateUrl: 'docs/views/main.html',
            link: function(scope, elem, attrs) {
                scope.scrollTo = function(id) {
                    $location.hash(id);
                    $anchorScroll();
                };
            }
        };
    }

    app.directive('sdDocs', MainDocsView);
    app.directive('prettyprint', function() {
        return {
            restrict: 'C',
            link: function postLink(scope, element, attrs) {
                var langExtension = attrs['class'].match(/\blang(?:uage)?-([\w.]+)(?!\S)/);
                if (langExtension) {
                    langExtension = langExtension[1];
                }
                element.html(window.prettyPrintOne(_.escape(element.html()), langExtension, true));
            }

        };
    });

    return app;

})();
