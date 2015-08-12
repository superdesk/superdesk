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

            /**
             * Highlight next matching string
             */
            scope.next = function() {
                editor.selectNext();
            };

            /**
             * Highlight previous matching string
             */
            scope.prev = function() {
                editor.selectPrev();
            };

            /**
             * Replace currently highlighted matching string with text
             */
            scope.replace = function() {
                editor.replace(scope.to || '');
                editor.selectNext();
            };

            /**
             * Replace all matching string with text
             */
            scope.replaceAll = function() {
                editor.replaceAll(scope.to || '');
            };

            scope.$watch('from', function(needle) {
                var input = document.getElementById('find-replace-what');
                var selectionStart = input.selectionStart;
                var selectionEnd = input.selectionEnd;

                editor.setSettings({findreplace: {needle: needle}});
                editor.render();
                editor.selectNext();
                input.setSelectionRange(selectionStart, selectionEnd);
            });

            scope.$on('$destroy', function() {
                editor.setSettings({findreplace: null});
                editor.render();
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
                display: {authoring: true, packages: false, legalArchive: false}
            });
    }]);

})();
