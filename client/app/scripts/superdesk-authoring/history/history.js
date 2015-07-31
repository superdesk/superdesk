(function() {

'use strict';

HistoryController.$inject = ['$scope', 'authoring', 'api', 'notify', 'desks'];
function HistoryController($scope, authoring, api, notify, desks) {
    $scope.last = null;
    $scope.versions = null;
    $scope.selected = null;
    $scope.users = null;
    $scope.desks = null;
    $scope.stages = null;

    function typeName(itemType) {
        if (itemType === 'text') {
            return 'Story';
        }
        return _.capitalize(itemType);
    }

    function fetchHistory() {
        desks.initialize()
            .then(function() {
                $scope.desks = desks.desks;
                $scope.stages = desks.deskStages;
                $scope.users = desks.users;
                $scope.canRevert = authoring.isEditable($scope.item) && !authoring.isPublished($scope.item);
                return api.archive.getByUrl($scope.item._links.self.href + '?version=all&embedded={"user":1}')
                .then(function(result) {
                    _.each(result._items, function(version) {
                        if (version.task) {
                            if (version.task.desk) {
                                var versiondesk = desks.deskLookup[version.task.desk];
                                version.desk = versiondesk && versiondesk.name;
                            }
                            if (version.task.stage) {
                                var versionstage = desks.stageLookup[version.task.stage];
                                version.stage = versionstage && versionstage.name;
                            }
                        }
                        if (version.version_creator || version.original_creator) {
                            var versioncreator = desks.userLookup[version.version_creator || version.original_creator];
                            version.creator = versioncreator && versioncreator.display_name;
                        }
                        version.typeName = typeName(version.type);
                    });
                    $scope.versions = _.sortBy(result._items, '_current_version');
                    $scope.last = lastVersion();

                    if ($scope.item._autosave) {
                        $scope.selected = $scope.item._autosave;
                    } else {
                        $scope.openVersion($scope.last);
                    }
                });
            });
    }

    /**
     * Get latest version from the list
     */
    function lastVersion() {
        if ($scope.item._latest_version) {
            return _.find($scope.versions._items, {_current_version: $scope.item._latest_version});
        }

        return _.max($scope.versions._items, function(version) {
            return version._current_version || version.version || version._updated;
        });
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

angular.module('superdesk.authoring.history', [])
    .config(['authoringWidgetsProvider', function(authoringWidgetsProvider) {
        authoringWidgetsProvider
            .widget('history', {
                icon: 'revision',
                label: gettext('History'),
                template: 'scripts/superdesk-authoring/history/views/history.html',
                order: 4,
                side: 'right',
                display: {authoring: true, packages: true}
            });
    }])

    .controller('HistoryWidgetCtrl', HistoryController);

})();
