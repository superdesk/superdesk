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

WidgetsManagerCtrl.$inject = ['$scope', '$routeParams', 'authoringWidgets'];
function WidgetsManagerCtrl($scope, $routeParams, authoringWidgets) {
    $scope.active = null;

    $scope.$watch('item', function(item) {
        if (!item) {
            $scope.widgets = null;
            return;
        }

        var display = item.type === 'composite' ? 'packages' : 'authoring';
        $scope.widgets = authoringWidgets.filter(function(widget) {
            return !!widget.display[display];
        });
    });

    $scope.isLocked = function(widget) {
        return widget.needUnlock && $scope.item._locked;
    };

    $scope.activate = function(widget) {
        if (!$scope.isLocked(widget)) {
            $scope.active = $scope.active === widget ? null : widget;
        }
    };

    this.activate = function(widget) {
        $scope.activate(widget);
    };

    $scope.closeWidget = function(widget) {
        $scope.active = null;
    };

    // activate widget based on query string
    angular.forEach($scope.widgets, function(widget) {
        if ($routeParams[widget._id]) {
            $scope.activate(widget);
        }
    });

    $scope.$watch('item._locked', function() {
        if ($scope.active) {
            var widget = $scope.active;
            $scope.closeWidget(widget);
            $scope.activate(widget);
        }
    });
}

function AuthoringWidgetsDir() {
    return {
        controller: WidgetsManagerCtrl,
        templateUrl: 'scripts/superdesk-authoring/widgets/views/authoring-widgets.html',
        transclude: true
    };
}

angular.module('superdesk.authoring.widgets', [])
    .provider('authoringWidgets', AuthoringWidgetsProvider)
    .directive('sdAuthoringWidgets', AuthoringWidgetsDir);

})();
