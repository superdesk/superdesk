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
    $scope.active = {
        left: null,
        right: null
    };

    $scope.widgets = authoringWidgets;

    $scope.activate = function(widget) {
        if (!widget.needUnlock || !$scope.item._locked) {
            $scope.active[widget.side] = $scope.active[widget.side] === widget ? null : widget;
        }
    };

    $scope.closeWidget = function(widget) {
        $scope.active[widget.side] = null;
    };

    // activate widget based on query string
    angular.forEach($scope.widgets, function(widget) {
        if ($routeParams[widget._id]) {
            $scope.activate(widget);
        }
    });

    $scope.$watch('item._locked', function() {
        var widget;
        _.each(['left', 'right'], function(side) {
            if ($scope.active[side]) {
                widget = $scope.active[side];
                $scope.closeWidget(widget);
                $scope.activate(widget);
            }
        });
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
