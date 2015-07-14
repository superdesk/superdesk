(function() {

'use strict';

MacrosService.$inject = ['api', 'autosave', 'notify'];
function MacrosService(api, autosave, notify) {
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

    function triggerMacro(macro, item, commit) {
        return api.save('macros', {
            macro: macro.name,
            item: _.omit(item), // get all the properties as shallow copy
            commit: !!commit
        }).then(function(res) {
            angular.extend(item, res.item);
            if (!commit) {
                autosave.save(item);
            }
            return item;
        }, function(err) {
            if (angular.isDefined(err.data._message)) {
                notify.error(gettext('Error: ' + err.data._message));
            }
        });
    }
}

MacrosController.$inject = ['$scope', 'macros', 'desks'];
function MacrosController($scope, macros, desks) {
    macros.get().then(function() {
        var currentDeskId = desks.getCurrentDeskId();
        if (currentDeskId !== null) {
            macros.getByDesk(desks.getCurrentDesk().name).then(function(_macros) {
                $scope.macros = _macros;
            });
        } else {
            $scope.macros = macros.macros;
        }
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
                order: 6,
                side: 'right',
                display: {authoring: true, packages: true}
            });
    }]);
})();
