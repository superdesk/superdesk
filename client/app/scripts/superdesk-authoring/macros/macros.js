(function() {

'use strict';

MacrosService.$inject = ['api', 'autosave'];
function MacrosService(api, autosave) {
    this.get = function() {
        return api.query('macros')
            .then(angular.bind(this, function(macros) {
                this.macros = macros._items;
                return this.macros;
            }));
    };

     this.getByDesk = function(desk) {
        return api.query('macros', {'desk': desk})
            .then(angular.bind(this, function(macros) {
                this.macros = macros._items;
                return this.macros;
            }));
    };

    this.setupShortcuts = function ($scope) {
        this.get().then(function(macros) {
            angular.forEach(macros, function(macro) {
                if (macro.shortcut) {
                    $scope.$on('key:ctrl:' + macro.shortcut, function() {
                        triggerMacro(macro, $scope.item);
                    });
                }
            });
        });
    };

    this.call = triggerMacro;

    function triggerMacro(macro, item) {
        return api.save('macros', {
            macro: macro.name,
            item: _.omit(item) // get all the properties as shallow copy
        }).then(function(res) {
            angular.extend(item, res.item);
            autosave.save(item);
            return item;
        });
    }
}

MacrosController.$inject = ['$scope', 'macros'];
function MacrosController($scope, macros) {

    macros.get().then(function() {
        $scope.macros = macros.macros;
    });

    $scope.call = function(macro) {
        return macros.call(macro, $scope.item);
    };
}

angular.module('superdesk.authoring.macros', [])

    .service('macros', MacrosService)
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
