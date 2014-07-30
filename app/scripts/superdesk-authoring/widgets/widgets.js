
'use strict';

function WidgetsManager($scope, widgets) {
    $scope.active = null;
    $scope.widgets = widgets;

    $scope.activate = function(widget) {
        $scope.active = $scope.active === widget ? null : widget;
    };
}

function AuthoringWidgetsDir() {
    return {
        controller: WidgetsManager,
        templateUrl: 'scripts/superdesk-authoring/widgets/views/authoring-widgets.html',
        scope: {item: '='},
        transclude: true,
        link: function(scope, elem) {

        }
    };
}

angular.module('superdesk.authoring.widgets', [])
    .directive('sdAuthoringWidgets', AuthoringWidgetsDir);
