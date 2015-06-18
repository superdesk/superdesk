(function() {
    'use strict';

    LegalArchiveService.$inject = ['$q', 'api', 'notify'];
    function LegalArchiveService($q, api, notify) {
        var DEFAULT_PAGE = 1;
        var DEFAULT_PER_PAGE = 25;

        this.query = function query(search, page, perPage) {
            console.log(search);

            page = page || DEFAULT_PAGE;
            perPage = perPage || DEFAULT_PER_PAGE;

            var criteria = {
                max_results: perPage,
                page: page
            };

            var where = [];

            _.forEach(search, function(n, key) {
                var val = _.trim(n);
                if (val) {
                    var clause = {};
                    clause[key] = {'$regex': val, '$options': '-i'};
                    where.push(clause);
                }
            });

            if (_.any(where)) {
                criteria.where = JSON.stringify({
                    '$or': where
                });
            }

            console.log(criteria);
            return api.legal_archive.query(criteria);
        };
    }

    LegalArchiveController.$inject = ['$scope', '$location', 'legal'];
    function LegalArchiveController($scope, $location, legal) {
        $scope.criteria = {};
        var default_items = Object.freeze({_meta: {max_results: 25, page: 1, total: 1}});
        $scope.items = default_items;
        $scope.loading = false;
        $scope.selected = {};

        $scope.search = function () {
            $scope.loading = true;
            legal.query($scope.criteria).then(function(items) {
                $scope.loading = false;
                $scope.items = items;
            });
        };

        $scope.preview = function(selectedItem) {
            console.log(selectedItem);
            $scope.selected.preview = selectedItem;
        };

        $scope.openLightbox = function () {
            $scope.selected.view = $scope.selected.preview;
        };

        $scope.closeLightbox = function () {
            $scope.selected.view = null;
        };

        $scope.clear = function () {
            $scope.criteria = {};
            $scope.items = default_items;
        };

        $scope.search();
    }

    var app = angular.module('superdesk.legal_archive', [
        'superdesk.activity',
        'superdesk.api'
    ]);

    app
        .service('legal', LegalArchiveService)
        .config(['apiProvider', function(apiProvider) {
            apiProvider.api('legal_archive', {
                type: 'http',
                backend: {rel: 'legal_archive'}
            });
            apiProvider.api('legal_archive_versions', {
                type: 'http',
                backend: {rel: 'legal_archive_versions'}
            });
        }])
        .config(['superdeskProvider', function(superdesk) {
            superdesk
                .activity('/legal_archive/', {
                    label: gettext('Legal Archive'),
                    description: gettext('Confidential data'),
                    priority: 100,
                    beta: true,
                    controller: LegalArchiveController,
                    templateUrl: 'scripts/superdesk-legal-archive/views/legal_archive.html',
                    category: superdesk.MENU_MAIN,
                    reloadOnSearch: false,
                    filters: [],
                    privileges: {legal_archive: 1}
                });
        }]);

    return app;
})();
