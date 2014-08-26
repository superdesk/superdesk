
(function() {

'use strict';

MetadataCtrl.$inject = ['$scope'];
function MetadataCtrl($scope) {

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
