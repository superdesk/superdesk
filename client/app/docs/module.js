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

    MainDocsView.$inject = [];
    function MainDocsView() {
        return {
            templateUrl: 'docs/views/main.html',
            link: function(scope, elem, attrs) {
            }
        };
    }
    app.directive('sdDocs', MainDocsView);

    return app;

})();
