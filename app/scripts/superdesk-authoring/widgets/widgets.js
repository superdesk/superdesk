(function() {

'use strict';

function AuthoringWidgetsProvider() {

    var widgets = [];

    this.widget = function(id, config) {
        widgets.push(angular.extend({ // make a new instance for every widget
        }, config, {_id: id}));
    };

    this.$get = function() {
        return widgets;
    };
}

WidgetsManagerCtrl.$inject = ['$scope', 'authoringWidgets'];
function WidgetsManagerCtrl($scope, authoringWidgets) {
    $scope.active = null;
    $scope.widgets = authoringWidgets;

    $scope.activate = function(widget) {
        $scope.active = $scope.active === widget ? null : widget;
    };
}

function AuthoringWidgetsDir() {
    return {
        controller: WidgetsManagerCtrl,
        templateUrl: 'scripts/superdesk-authoring/widgets/views/authoring-widgets.html',
        scope: {item: '='},
        transclude: true
    };
}

angular.module('superdesk.authoring.widgets', [])
    .provider('authoringWidgets', AuthoringWidgetsProvider)
    .directive('sdAuthoringWidgets', AuthoringWidgetsDir);

})();
