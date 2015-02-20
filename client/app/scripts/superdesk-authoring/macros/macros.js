(function() {

'use strict';

MacrosController.$inject = ['$scope', 'api', 'autosave'];
function MacrosController($scope, api, autosave) {

    api.query('macros').then(function(macros) {
        $scope.macros = macros._items;
    });

    $scope.call = function(macro) {
        api.save('macros', {
            macro: macro.name,
            item: _.omit($scope.item) // get all the properties as shallow copy
        }).then(function(res) {
            angular.extend($scope.item, res.item);
            autosave.save($scope.item);
        });
    };
}

angular.module('superdesk.authoring.macros', ['superdesk.authoring'])

    .controller('Macros', MacrosController)

    .config(['authoringWidgetsProvider', function(authoringWidgetsProvider) {
        authoringWidgetsProvider
            .widget('macros', {
                icon: 'macros',
                label: gettext('Macros'),
                template: 'scripts/superdesk-authoring/macros/views/macros-widget.html',
                side: 'right',
                display: {authoring: true, packages: true}
            });
    }]);
})();
