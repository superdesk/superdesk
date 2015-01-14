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

var TEXT_TYPE = 3;

function EditorService() {

    this.clear = function() {
        this.elem = null;
        this.editor = null;
        this.readOnly = false;
    };

    /**
     * Start a command for an active editor
     */
    this.startCommand = function() {
        this.readOnly = true;
        this.command = new FindReplaceCommand(this.elem);
        // prevent edits while command is active
        angular.element(this.elem).on('keydown', function(event) {
            event.preventDefault();
            return false;
        });
    };

    /**
     * Stop active command
     */
    this.stopCommand = function() {
        this.command.finish();
        this.command = null;
        this.readOnly = false;
        // stop preventing edits
        angular.element(this.elem).off('keydown');
        // trigger a blur on elem to trigger a save
        _.defer(function(elem) {
            angular.element(elem).blur();
        }, this.elem);
    };

    this.clear(); // init
}

function FindReplaceCommand(rootNode) {
    var matches = 0, current, needle, replacements, html = angular.element(rootNode).html();

    /**
     * Find a given string within editor
     */
    this.find = function(_needle) {
        clearHighlights();
        needle = _needle;
        matches = 0;
        current = 0;
        replacements = {};
        if (needle) {
            find(rootNode);
        }

        return matches;
    };

    /**
     * Highlight next match
     */
    this.next = function() {
        clearHighlights();
        current = (current + 1) % matches;
        matches = 0;
        find(rootNode);
    };

    /**
     * Highlight previous match
     */
    this.prev = function() {
        clearHighlights();
        current = current === 0 ? matches - 1 : current - 1;
        matches = 0;
        find(rootNode);
    };

    /**
     * Replace current match with given string
     */
    this.replace = function(replaceWith) {
        if (current != null) {
            var oldMatches = matches;

            // do replacement
            clearHighlights();
            matches = 0;
            replacements[current] = replaceWith || '';
            find(rootNode, true);
            html = angular.element(rootNode).html();

            // highlight rest
            matches = 0;
            current = current % (oldMatches - 1);
            replacements = {};
            find(rootNode);
            return matches;
        }
    };

    /**
     * Replace all matches with given string
     */
    this.replaceAll = function(replaceWith) {
        for (var i = 0; i < matches; i++) {
            replacements[i] = replaceWith || '';
        }

        clearHighlights();
        matches = 0;
        find(rootNode, true);
        html = angular.element(rootNode).html();
    };

    /**
     * Remove any left hightlights - called on exit
     */
    this.finish = function() {
        clearHighlights();
    };

    function find(node, stopHighlight) {
        if (node.nodeType === TEXT_TYPE) {
            var color,
                selection = document.getSelection(),
                index = node.wholeText.indexOf(needle),
                offset = 0;
            while (index > -1) {
                color = getColor(current != null ? current === matches : matches === 0);
                offset = index + needle.length;

                var range = document.createRange();
                range.setStart(node, index);
                range.setEnd(node, index + needle.length);
                selection.removeAllRanges();
                selection.addRange(range);

                if (replacements[matches] != null) {
                    document.execCommand('insertText', false, replacements[matches]);
                } else if (!stopHighlight) {
                    var oldLength = node.wholeText.length;
                    document.execCommand('hiliteColor', false, color);
                    if (oldLength > node.wholeText.length) {
                        offset = 0; // hilite split node text so do lookup from 0
                    }
                }

                matches++; // do the count now so we can use it as 0-based index
                index = node.wholeText.indexOf(needle, offset);
            }

            selection.removeAllRanges();
        } else {
            angular.forEach(node.childNodes, function(node) {
                find(node, stopHighlight);
            });
        }
    }

    function getColor(isCurrent) {
        return isCurrent ? '#edd400' : '#d3d7cf';
    }

    function clearHighlights() {
        angular.element(rootNode).html(html);
    }
}

angular.module('superdesk.editor', [])

    .service('editor', EditorService)

    .directive('sdTextEditor', ['editor', function (editor) {

        var config = {
            buttons: ['bold', 'italic', 'underline', 'quote', 'anchor'],
            anchorInputPlaceholder: gettext('Paste or type a full link')
        };

        /**
         * Get number of lines for all p nodes before given node withing same parent.
         */
        function getLinesBeforeNode(node) {
            var lines = 0;
            var p = node.previousSibling;
            while (p) {
                if (p.childNodes.length && p.childNodes[0].nodeType === TEXT_TYPE) {
                    lines += p.childNodes[0].wholeText.split('\n').length;
                } else if (p.childNodes.length) {
                    lines += 1; // empty paragraph
                }
                p = p.previousSibling;
            }

            return lines;
        }

        /**
         * Get line/column coordinates for given cursor position.
         */
        function getLineColumn() {
            var text, lines, linesBefore;
            var selection = window.getSelection();
            if (selection.anchorNode.nodeType === TEXT_TYPE) {
                text = selection.anchorNode.wholeText.substring(0, selection.anchorOffset);
                lines = text.split('\n');
                linesBefore = getLinesBeforeNode(selection.anchorNode.parentNode);
            } else {
                text = '';
                lines = [text];
                linesBefore = getLinesBeforeNode(selection.anchorNode);
            }
            return {
                line: lines.length + linesBefore,
                column: lines[lines.length - 1].length + 1
            };
        }

        return {
            scope: {type: '='},
            require: 'ngModel',
            templateUrl: 'scripts/superdesk/editor/views/editor.html',
            link: function(scope, elem, attrs, ngModel) {

                var editorElem;

                function updateModel() {
                    if (editor.readOnly) {
                        return;
                    }

                    scope.$apply(function editorModelUpdate() {
                        ngModel.$setViewValue(editorElem.html());
                    });
                }

                ngModel.$render = function renderEditor() {
                    editorElem = elem.find(scope.type === 'preformatted' ?  '.editor-type-text' : '.editor-type-html');
                    editorElem.empty();
                    editorElem.html(ngModel.$viewValue || '<p></p>');

                    editor.elem = editorElem[0];
                    editor.editor = new window.MediumEditor(editor.elem, config);

                    editorElem.on('input', updateModel);
                    editorElem.on('blur', updateModel);

                    if (scope.type === 'preformatted') {
                        editorElem.on('keydown keyup click', function() {
                            scope.$apply(function() {
                                angular.extend(scope.cursor, getLineColumn());
                            });
                        });
                    }

                    scope.$on('$destroy', function() {
                        editorElem.off();
                        editor.clear();
                    });

                    scope.cursor = {};
                };
            }
        };
    }]);

})();
