(function() {

'use strict';

HistoryController.$inject = ['$scope', 'authoring', 'api', 'notify', 'desks', 'archiveService'];
function HistoryController($scope, authoring, api, notify, desks, archiveService) {
    $scope.last = null;
    $scope.versions = null;
    $scope.selected = null;
    $scope.users = null;
    $scope.desks = null;
    $scope.stages = null;

    function fetchHistory() {
        desks.initialize()
            .then(function() {
                $scope.desks = desks.desks;
                $scope.stages = desks.deskStages;
                $scope.users = desks.users;

                archiveService.getVersionHistory($scope.item, desks, 'operations').then(function(versions) {
                    $scope.versions = versions;
                    $scope.last = archiveService.lastVersion($scope.item, $scope.versions);

                    _.forEach($scope.versions, function(version) {
                        if (version.operation === 'publish') {
                            version.show_sent_to = false;
                            fetchItemPublishQueue(version).then(function(queue) {
                                version.queuedItems = queue._items;
                            });
                        }
                    });

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

    function fetchItemPublishQueue (version) {
        var criteria = {'item_id': version._id, 'item_version': $scope.item._current_version, 'max_results': 20};

        return api.publish_queue.query(criteria);
    }

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

    $scope.$watchGroup(['item._id', 'item._latest_version'], fetchHistory);
}

versioningHistoryDirective.$inject = [];
function versioningHistoryDirective() {
    return {
        templateUrl: 'scripts/superdesk-authoring/versioning/history/views/history.html'
    };
}

angular.module('superdesk.authoring.versioning.history', [])
    .directive('sdVersioningHistory', versioningHistoryDirective)
    .controller('HistoryWidgetCtrl', HistoryController);
})();
