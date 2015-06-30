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
            };

            scope.$watch('from', function(needle) {
                var input = document.getElementById('find-replace-what'),
                    selectionStart = input.selectionStart,
                    selectionEnd = input.selectionEnd;
                editor.command.find(needle);
                input.setSelectionRange(selectionStart, selectionEnd);
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
                order: 2,
                side: 'right',
                needUnlock: true,
                display: {authoring: true, packages: false}
            });
    }]);

})();
