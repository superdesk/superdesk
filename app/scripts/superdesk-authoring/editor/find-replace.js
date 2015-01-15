/**
 * This file is part of Superdesk.
 *
 * Copyright 2013, 2014 Sourcefabric z.u. and contributors.
 *
 * For the full copyright and license information, please see the
 * AUTHORS and LICENSE files distributed with this source code, or
 * at https://www.sourcefabric.org/superdesk/license
 */
(function() {

'use strict';

FindReplaceController.$inject = ['$scope', 'editor'];
function FindReplaceController($scope, editor) {

    $scope.to = '';
    $scope.from = '';

    $scope.next = function() {
        editor.command.next();
    };

    $scope.prev = function() {
        editor.command.prev();
    };

    $scope.replace = function() {
        editor.command.replace($scope.to || '');
    };

    $scope.replaceAll = function() {
        editor.command.replaceAll($scope.to || '');
        $scope.closeWidget();
    };

    $scope.$watch('from', function(needle) {
        editor.command.find(needle);
    });

    editor.startCommand();
    $scope.$on('$destroy', function() {
        editor.stopCommand();
    });
}

angular.module('superdesk.authoring.find-replace', ['superdesk.editor', 'superdesk.authoring.widgets'])
    .controller('findReplace', FindReplaceController)
    .config(['authoringWidgetsProvider', function(authoringWidgetsProvider) {
        authoringWidgetsProvider
            .widget('find-replace', {
                icon: 'search',
                label: gettext('Find and Replace'),
                template: 'scripts/superdesk-authoring/editor/views/find-replace.html',
                side: 'right'
            });
    }]);

})();
