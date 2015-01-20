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

FindReplaceDirective.$inject = ['$timeout', '$rootScope', 'editor'];
/**
 * using directive here so that it can return focus
 */
function FindReplaceDirective($timeout, $rootScope, editor) {
    return {
        controller: function($scope) {
        },
        link: function(scope, elem) {
            scope.to = '';
            scope.from = '';

            scope.next = function() {
                editor.command.next();
            };

            scope.prev = function() {
                editor.command.prev();
            };

            scope.replace = function() {
                editor.command.replace(scope.to || '');
            };

            scope.replaceAll = function() {
                editor.command.replaceAll(scope.to || '');
                scope.closeWidget(scope.widget);
            };

            scope.$watch('from', function(needle) {
                editor.command.find(needle);

                // return focus to input - just focus() doesn't work here for some reason
                var input = document.getElementById('find-replace-what');
                input.focus();
                input.select();
                document.getSelection().collapseToEnd();
            });

            editor.startCommand();
            scope.$on('$destroy', function() {
                editor.stopCommand();
            });
        }
    };
}

angular.module('superdesk.authoring.find-replace', ['superdesk.editor', 'superdesk.authoring.widgets'])
    .directive('sdFindReplace', FindReplaceDirective)
    .config(['authoringWidgetsProvider', function(authoringWidgetsProvider) {
        authoringWidgetsProvider
            .widget('find-replace', {
                icon: 'find-replace',
                label: gettext('Find and Replace'),
                template: 'scripts/superdesk-authoring/editor/views/find-replace.html',
                side: 'right',
                display: {authoring: true, packages: false}
            });
    }]);

})();
