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

WidgetsManagerCtrl.$inject = ['$scope', '$routeParams', 'authoringWidgets', 'archiveService', 'keyboardManager', '$location'];
function WidgetsManagerCtrl($scope, $routeParams, authoringWidgets, archiveService, keyboardManager, $location) {
    $scope.active = null;

    $scope.$watch('item', function(item) {
        if (!item) {
            $scope.widgets = null;
            return;
        }

        var display;

        if (archiveService.isLegal(item)) {
            display = 'legalArchive';
        } else if (archiveService.isArchived(item)) {
            display = 'archived';
        } else {
            display = item.type === 'composite' ? 'packages' : item.state === 'killed' ? 'killedItem' : 'authoring';
        }

        $scope.widgets = authoringWidgets.filter(function(widget) {
            return !!widget.display[display];
        });

        /*
         * Navigate throw right tab widgets with keyboard combination
         * Combination: Ctrl + {{widget number}}
         */
        angular.forEach(_.sortBy($scope.widgets, 'order'), function (widget, index) {
            keyboardManager.bind('ctrl+' + (index + 1), function () {
                $scope.activate(widget);
            }, {inputDisabled: false, group: gettext('Authoring'), description: gettext('Toggles widget')});
            if ($location.search()[widget._id]) {
                $scope.activate(widget);
            }
        });
    });

    $scope.isLocked = function(widget) {
        return (widget.needUnlock && $scope.item._locked) ||
        (widget.needEditable && !$scope.item._editable);
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
AuthoringWidgetsDir.$inject = ['desks'];
function AuthoringWidgetsDir(desks) {
    return {
        controller: WidgetsManagerCtrl,
        templateUrl: 'scripts/superdesk-authoring/widgets/views/authoring-widgets.html',
        transclude: true,
        link: function (scope, elem) {
            scope.userLookup = desks.userLookup;
            var editor = elem.find('.page-content-container'),
                stickyHeader = elem.find('.authoring-sticky');

            editor.on('scroll', function () {
                if (editor.scrollTop() > 5) {
                    stickyHeader.addClass('authoring-sticky--fixed');
                } else {
                    stickyHeader.removeClass('authoring-sticky--fixed');
                }
            });
        }
    };
}

angular.module('superdesk.authoring.widgets', [])
    .provider('authoringWidgets', AuthoringWidgetsProvider)
    .directive('sdAuthoringWidgets', AuthoringWidgetsDir);

})();
