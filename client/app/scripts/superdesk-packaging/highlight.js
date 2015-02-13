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

    HighlightsService.$inject = ['api', '$q', 'packagesService'];
    function HighlightsService(api, $q, packagesService) {
        this.createEmptyHighlight = function createEmptyHighlight(highlight) {
            var pkg_defaults = {
                headline: highlight.name || '',
                highlight: highlight._id || ''
            };

            return packagesService.createEmptyPackage(pkg_defaults);
        };
    }

    var app = angular.module('superdesk.highlight', [
        'superdesk.packaging',
        'superdesk.activity',
        'superdesk.api'
    ]);

    app
    .service('highlightsService', HighlightsService)
    .config(['superdeskProvider', function(superdesk) {
        superdesk
        .activity('create.highlight', {
            label: gettext('Create highlight'),
            controller: ['data', 'highlightsService', 'superdesk',
                function(data, highlightsService, superdesk) {
                    if (data) {
                        highlightsService.createEmptyHighlight(data).then(
                            function(new_package) {
                            superdesk.intent('author', 'package', new_package);
                        });
                    } else {
                        superdesk.intent('create', 'package');
                    }
            }],
            filters: [
                {action: 'create', type: 'highlight'}
            ]
        });
    }]);

    return app;
})();
