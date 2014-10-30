(function() {

'use strict';

    VersioningController.$inject = ['$scope', 'api', '$location', 'notify', 'workqueue', 'lock'];
    function VersioningController($scope, api, $location, notify, workqueue, lock) {

        $scope.last = null;
        $scope.versions = null;
        $scope.selected = null;
        $scope.users = {};

        function fetchUser(id) {
            api.users.getById(id)
            .then(function(result) {
                $scope.users[id] = result;
            });
        }

        function fetchVersions() {
            return api.archive.getByUrl($scope.item._links.self.href + '?version=all&embedded={"user":1}')
            .then(function(result) {
                _.each(result._items, function(version) {
                    var creator = version.creator || version.original_creator;
                    if (creator && !$scope.users[creator]) {
                        fetchUser(creator);
                    }
                });

                $scope.versions = result;
                $scope.selected = $scope.item._autosave ? $scope.item._autosave : lastVersion();
                $scope.last = lastVersion();

            });
        }

        /**
         * Get latest version from the list
         */
        function lastVersion() {
            if ($scope.item._latest_version) {
                return _.find($scope.versions._items, {_version: $scope.item._latest_version});
            }

            return _.max($scope.versions._items, function(version) {
                return version._version || version.version || version._updated;
            });
        }

        /**
         * Open autosaved version
         */
        $scope.openAutosave = function() {
            $scope.selected = $scope.item._autosave;
            $scope.closePreview();
        };

        /**
         * Open given version for preview
         *
         * If there is no autosave then last one will make item editable
         */
        $scope.openVersion = function(version) {
            $scope.selected = version;
            if (version === $scope.last && !$scope.item._autosave) {
                $scope.closePreview();
            } else {
                $scope.preview(version);
            }
        };

        /**
         * Revert to given version
         *
         * If the version is the last one and there is an autosave - drop autosave
         */
        $scope.revert = function(version) {
            $scope.$parent.revert(version).then(fetchVersions);
        };

        $scope.$watchGroup(['item._id', 'item._latest_version'], fetchVersions);
    }

angular.module('superdesk.authoring.versions', [])
    .config(['authoringWidgetsProvider', function(authoringWidgetsProvider) {
        authoringWidgetsProvider
            .widget('versions', {
                icon: 'revision',
                label: gettext('Versions'),
                template: 'scripts/superdesk-authoring/versioning/views/versions.html'
            });
    }])

    .controller('VersioningWidgetCtrl', VersioningController);

})();
