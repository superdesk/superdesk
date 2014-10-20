
(function() {

'use strict';

MetadataCtrl.$inject = ['$scope', 'desks'];
function MetadataCtrl($scope, desks) {
    desks.initialize()
    .then(function() {
        $scope.deskLookup = desks.deskLookup;
        $scope.userLookup = desks.userLookup;
    });
}

angular.module('superdesk.authoring.metadata', ['superdesk.authoring.widgets'])
    .config(['authoringWidgetsProvider', function(authoringWidgetsProvider) {
        authoringWidgetsProvider
            .widget('metadata', {
                icon: 'info',
                label: gettext('Info'),
                template: 'scripts/superdesk-authoring/metadata/views/metadata-widget.html',
                order: 1
            });
    }])

    .controller('MetadataWidgetCtrl', MetadataCtrl);

})();
