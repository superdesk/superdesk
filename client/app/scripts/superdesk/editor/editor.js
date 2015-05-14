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

var TEXT_TYPE = 3,
    MARKER_CLASS = 'sdmark';

function click(target) {
    target.dispatchEvent(new MouseEvent('click'));
}

function EditorService() {

    /**
     * Store current anchor position within given node
     */
    this.storeSelection = function storeSelection(node) {
        var selection = document.getSelection();
        if (selection.anchorNode == null || selection.anchorNode.nodeType !== TEXT_TYPE) {
            return;
        }

        var next = selection.anchorNode.splitText(selection.anchorOffset),
            span = document.createElement('span');
        span.classList.add(MARKER_CLASS);
        selection.anchorNode.parentNode.insertBefore(span, next);
    };

    /**
     * Reset stored anchor position in given node
     */
    this.resetSelection = function resetSelection(node, data) {
        var marks = node.getElementsByClassName(MARKER_CLASS),
            selection = document.getSelection(),
            range = document.createRange();

        if (selection.rangeCount) {
            selection.removeAllRanges();
        }

        while (marks.length) {
            var mark = marks.item(0);
            range.setStartBefore(mark);
            selection.addRange(range);
            mark.parentNode.removeChild(mark);
        }
    };

    this.clear = function() {
        this.elem = null;
        this.editor = null;
        this.readOnly = false;
    };

    function preventEditing(event) {
        event.preventDefault();
        return false;
    }

    this.disableEditorToolbar = function disableEditorToolbar() {
        if (this.editor) {
            this.editor.toolbar.toolbar.classList.add('ng-hide');
        }
    };

    this.enableEditorToolbar = function enableEditorToolbar() {
        if (this.editor) {
            this.editor.toolbar.toolbar.classList.remove('ng-hide');
        }
    };

    /**
     * Start a command for an active editor
     */
    this.startCommand = function() {
        this.readOnly = true;
        this.command = new FindReplaceCommand(this.elem);
        angular.element(this.elem).on('keydown', preventEditing);
        this.disableEditorToolbar();
    };

    /**
     * Stop active command
     */
    this.stopCommand = function() {
        this.command.finish();
        this.command = null;
        this.readOnly = false;
        angular.element(this.elem).off('keydown', preventEditing);
        this.enableEditorToolbar();
        this.triggerModelUpdate();
    };

    this.triggerModelUpdate = function() {
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

    .directive('sdTextEditor', ['editor', 'spellcheck', '$timeout', function (editor, spellcheck, $timeout) {

        var config = {
            buttons: ['bold', 'italic', 'underline', 'quote', 'anchor'],
            anchorInputPlaceholder: gettext('Paste or type a full link'),
            disablePlaceholders: true
        };

        /**
         * Get number of lines for all p nodes before given node withing same parent.
         */
        function getLinesBeforeNode(p) {

            function getLineCount(text) {
                return text.split('\n').length;
            }

            var lines = 0;
            while (p) {
                if (p.childNodes.length && p.childNodes[0].nodeType === TEXT_TYPE) {
                    lines += getLineCount(p.childNodes[0].wholeText);
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
            var column, lines,
                selection = window.getSelection();
            if (selection.anchorNode.nodeType === TEXT_TYPE) {
                var text = selection.anchorNode.wholeText.substring(0, selection.anchorOffset);
                var node = selection.anchorNode;
                column = text.length + 1;
                while (node.nodeName !== 'P') {
                    if (node.previousSibling) {
                        column += node.previousSibling.wholeText ?
                            node.previousSibling.wholeText.length :
                            node.previousSibling.textContent.length;
                        node = node.previousSibling;
                    } else {
                        node = node.parentNode;
                    }
                }

                lines = 0 + getLinesBeforeNode(node);
            } else {
                lines = 0 + getLinesBeforeNode(selection.anchorNode);
                column = 1;
            }

            return {
                line: lines,
                column: column
            };
        }

        return {
            scope: {type: '=', config: '='},
            require: 'ngModel',
            templateUrl: 'scripts/superdesk/editor/views/editor.html',
            link: function(scope, elem, attrs, ngModel) {

                var editorElem,
                    updateTimeout,
                    renderTimeout;

                /**
                 * Remove spellcheck highlights from node
                 */
                function removeSpellcheck(node) {
                    var selection = editor.storeSelection(node),
                        html = spellcheck.clean(node);
                    node.innerHTML = html;
                    editor.resetSelection(node, selection);
                    return html;
                }

                function updateModel() {
                    if (editor.readOnly) {
                        return;
                    }

                    var html = removeSpellcheck(editorElem[0]);
                    scope.$applyAsync(function() {
                        ngModel.$setViewValue(html);
                        spellcheck.render(editorElem[0]);
                    });
                }

                ngModel.$viewChangeListeners.push(function renderSpellcheck() {
                    $timeout.cancel(renderTimeout);
                    renderTimeout = $timeout(function() {
                        spellcheck.render(editorElem[0]);
                    }, 200, false);
                });

                ngModel.$render = function renderEditor() {
                    editorElem = elem.find(scope.type === 'preformatted' ?  '.editor-type-text' : '.editor-type-html');

                    editorElem.empty();
                    editorElem.html(ngModel.$viewValue || '');

                    // this has to register before the editor
                    spellcheck.addEventListener(editorElem[0]);

                    var editorConfig = angular.extend({}, config, scope.config || {});
                    editor.elem = editorElem[0];
                    editor.editor = new window.MediumEditor(editor.elem, editorConfig);

                    editorElem.on('input', function(event) {
                        $timeout.cancel(updateTimeout);
                        updateTimeout = $timeout(updateModel, 300, false);
                    });

                    editorElem.on('contextmenu', function(event) {
                        if (spellcheck.isErrorNode(event.target)) {
                            var menu = elem[0].getElementsByClassName('dropdown-menu')[0],
                                toggle = elem[0].getElementsByClassName('dropdown-toggle')[0];
                            if (elem.find('.dropdown.open').length) {
                                click(toggle);
                            }

                            scope.suggestions = null;
                            spellcheck.suggest(event.target.textContent).then(function(suggestions) {
                                scope.suggestions = suggestions;
                                scope.replaceTarget = event.target;
                                $timeout(function() {
                                    menu.style.left = (event.target.offsetLeft) + 'px';
                                    menu.style.top = (event.target.offsetTop + event.target.offsetHeight) + 'px';
                                    menu.style.position = 'absolute';
                                    click(toggle);
                                }, 0, false);
                            });

                            return false;
                        }
                    });

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
                        spellcheck.removeEventListener(editorElem[0]);
                    });

                    scope.cursor = {};
                    spellcheck.render(editorElem[0]);
                };

                scope.replace = function(text) {
                    scope.replaceTarget.parentNode.replaceChild(document.createTextNode(text), scope.replaceTarget);
                };
            }
        };
    }]);

})();
