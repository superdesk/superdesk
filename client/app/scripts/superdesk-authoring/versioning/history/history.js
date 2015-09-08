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

VersioningHistoryDirective.$inject = [];
function VersioningHistoryDirective() {
    return {
        templateUrl: 'scripts/superdesk-authoring/versioning/history/views/history.html'
    };
}

TransmissionDetailsDirective.$inject = ['api', 'archiveService'];
function TransmissionDetailsDirective(api, archiveService) {
    return {
        templateUrl: 'scripts/superdesk-authoring/versioning/history/views/publish_queue.html',
        scope: {
            item: '='
        },
        link: function(scope) {
            scope.transmitted_item = null;
            scope.show_transmission_details = false;

            /**
             * Sets the model to be displayed in the modal-body.
             */
            scope.showFormattedItem = function(item) {
                scope.transmitted_item = item.formatted_item;
            };

            /**
             * Sets the model of the modal to null when and is hidden.
             */
            scope.hideFormattedItem = function() {
                scope.transmitted_item = null;
            };

            /**
             * Triggered when user clicks on +/- symbol in the Item History.
             *
             * When user clicks on + symbol, it hits the API to bring the transmission details from publish queue.
             */
            scope.showOrHideTransmissionDetails = function() {
                scope.show_transmission_details = !scope.show_transmission_details;

                if (scope.show_transmission_details) {
                    var criteria = {'max_results': 20};

                    criteria.where = JSON.stringify ({
                        '$and': [{'item_id': scope.item._id}, {'item_version': scope.item._current_version}]
                    });

                    var promise;

                    if (archiveService.isLegal(scope.item)) {
                        promise = api.legal_publish_queue.query(criteria);
                    } else {
                        promise = api.publish_queue.query(criteria);
                    }

                    promise.then(function(response) {
                        _.each(response._items, function(item) {
                            if (angular.isUndefined(item.completed_at)) {
                                item.completed_at = item._updated;
                            }
                        });

                        scope.queuedItems = response._items;
                    });
                }
            };
        }
    };
}

angular.module('superdesk.authoring.versioning.history', [])
    .directive('sdVersioningHistory', VersioningHistoryDirective)
    .directive('sdTransmissionDetails', TransmissionDetailsDirective)
    .controller('HistoryWidgetCtrl', HistoryController);
})();
