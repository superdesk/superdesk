
(function() {

'use strict';

    VersioningController.$inject = ['$scope', 'api', '$location', 'notify', 'workqueue'];
    function VersioningController($scope, api, $location, notify, workqueue) {

        $scope.versions = null;
        $scope.selected = null;
        $scope.users = {};

        var fetchUser = function(id) {
            api.users.getById(id)
            .then(function(result) {
                $scope.users[id] = result;
            });
        };

        var fetchVersions = function() {
            $scope.users = {};
            return api.archive.getByUrl($scope.item._links.self.href + '?version=all&embedded={"user":1}')
            .then(function(result) {
                _.each(result._items, function(version) {
                    var creator = version.creator || version.original_creator;
                    if (creator && !$scope.users[creator]) {
                        fetchUser(creator);
                    }
                });
                $scope.versions = result;
                $scope.selected = _.find($scope.versions._items, {_version: $scope.item._latest_version});
            });
        };
        fetchVersions();

        $scope.openVersion = function(version) {
            $scope.selected = version;
            $scope.item._version = version._version;
            $scope.item.headline = version.headline;
            $scope.item.body_html = version.body_html;
        };

        $scope.revert = function(version) {
            api.archive.replace($scope.item._links.self.href, {
                type: 'text',
                last_version: $scope.item._latest_version,
                old_version: version
            })
            .then(function(result) {
                notify.success(gettext('Item reverted.'));
                workqueue.update(result);
                $scope.openVersion(result);
                fetchVersions();
            }, function(result) {
                notify.error(gettext('Error. Item not reverted.'));
            });
        };
    }

angular.module('superdesk.authoring.versions', ['superdesk.authoring.versions'])
    .config(['authoringWidgetsProvider', function(authoringWidgetsProvider) {
        authoringWidgetsProvider
            .widget('versions', {
                icon: 'archive',
                label: gettext('Versions'),
                template: 'scripts/superdesk-authoring/versioning/views/versions.html'
            });
    }])

    .controller('VersioningWidgetCtrl', VersioningController);

})();
