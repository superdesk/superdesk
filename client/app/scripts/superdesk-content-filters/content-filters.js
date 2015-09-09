/**
 * This file is part of Superdesk.
 *
 * Copyright 2013, 2014, 2015 Sourcefabric z.ú. and contributors.
 *
 * For the full copyright and license information, please see the
 * AUTHORS and LICENSE files distributed with this source code, or
 * at https://www.sourcefabric.org/superdesk/license
 */

(function() {
    'use strict';

    var module;

    // TODO: change name etc... docstrings...
    ContentFiltersService.$inject = ['api', 'urls', 'session', '$q'];
    function ContentFiltersService(api, urls, session, $q) {

        this.fetch = function (success, error) {
            return session.getIdentity().then(function(identity) {
                return api.query('dictionaries', {
                    projection: {content: 0},
                    where: {
                        $or: [
                            {user: {$exists: false}},
                            {user: identity._id}
                        ]}
                })
                .then(success, error);
            });
        };
    }

    // TODO: docstring
    ContentFiltersConfigController.$inject = ['$scope'];
    function ContentFiltersConfigController ($scope) {

        console.log('Content Filters controller');
    }

    // TODO: docstring
    module = angular.module('superdesk.content_filters', []);

    module.config(['superdeskProvider', function (superdesk) {
            var templateUrl = 'scripts/superdesk-content-filters/' +
                              'views/settings.html';

            superdesk.activity('/settings/content-filters', {
                    label: gettext('Content Filters'),
                    controller: ContentFiltersConfigController,
                    templateUrl: templateUrl,
                    category: superdesk.MENU_SETTINGS,
                    priority: -800,
                    privileges: {dictionaries: 1}
                });
        }])
        .service('contentFilters', ContentFiltersService)
        .controller('contentFiltersConfigCtrl', ContentFiltersConfigController);
})();
