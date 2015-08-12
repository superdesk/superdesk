(function() {

'use strict';

VersioningController.$inject = ['$scope', 'authoring', 'api', 'notify', 'lock', 'desks', 'archiveService'];
function VersioningController($scope, authoring, api, notify, lock, desks, archiveService) {

    $scope.last = null;
    $scope.versions = null;
    $scope.selected = null;
    $scope.users = null;
    $scope.canRevert = false;
    $scope.desks = null;
    $scope.stages = null;

    function fetchVersions() {
        desks.initialize()
            .then(function() {
                $scope.desks = desks.desks;
                $scope.stages = desks.deskStages;
                $scope.users = desks.users;

                archiveService.getVersionHistory($scope.item, desks, 'versions').then(function(versions) {
                    $scope.versions = versions;
                    $scope.last = archiveService.lastVersion($scope.item, $scope.versions);

                    if (archiveService.isLegal($scope.item)) {
                        $scope.canRevert =  false;
                        $scope.openVersion($scope.last);
                    } else {
                        $scope.canRevert =  authoring.isEditable($scope.item) && !authoring.isPublished($scope.item);

                        if ($scope.item._autosave) {
                            $scope.selected = $scope.item._autosave;
                        } else {
                            $scope.openVersion($scope.last);
                        }
                    }
                });
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

versioningVersionDirective.$inject = [];
function versioningVersionDirective() {
    return {
        templateUrl: 'scripts/superdesk-authoring/versioning/versions/views/versions.html'
    };
}

angular.module('superdesk.authoring.versioning.versions', [])
    .directive('sdVersioningVersion', versioningVersionDirective)
    .controller('VersioningWidgetCtrl', VersioningController);
})();
