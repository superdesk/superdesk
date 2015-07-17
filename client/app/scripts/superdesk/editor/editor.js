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

function click(target) {
    target.dispatchEvent(new MouseEvent('click'));
}

function EditorService() {
    this.settings = {spellcheck: true};
    this.stopEvents = false;
    this.addEventListeners = addEventListeners;
    this.removeEventListeners = removeEventListeners;

    this.KEY_CODES = Object.freeze({
        Y: 89,
        X: 90
    });

    var vm = this;

    this.fieldStack = {};

    this.setInitialValue = function (key, initialValue) {
        vm.fieldStack[key] = {
            'stack': [],
            'index':0
        };
        vm.fieldStack[key].stack.push(initialValue);
    };

    this.savetoHistory = function(key, html) {
        vm.fieldStack[key].stack.push(html);
        vm.fieldStack[key].index = vm.fieldStack[key].stack.length - 1;
    };

    this.getInitialValue = function (key) {
        return vm.fieldStack[key].stack[0];
    };

    this.resetStack = function(key) {
        vm.fieldStack[key] = {};
    };

    this.getUndoViewValue = function(key) {
        var _undoValue;
        if (vm.fieldStack[key] != null) {
            if (vm.fieldStack[key].stack.length === 1) {
                _undoValue = vm.getInitialValue(key);
            } else {
                if (vm.fieldStack[key].stack[vm.fieldStack[key].index - 1] != null) {
                    if (vm.fieldStack[key].index === 1) {
                        _undoValue = vm.getInitialValue(key);
                    } else {
                        _undoValue = vm.fieldStack[key].stack[vm.fieldStack[key].index - 1];
                    }
                    vm.fieldStack[key].index -= 1;
                }
            }
        }
        return _undoValue;
    };

    this.getRedoViewValue = function(key) {
        var _redoValue;
        if (vm.fieldStack[key] != null) {
            if (vm.fieldStack[key].stack.length !== 0 && vm.fieldStack[key].stack[vm.fieldStack[key].index + 1] != null) {
                _redoValue = vm.fieldStack[key].stack[vm.fieldStack[key].index + 1];
                vm.fieldStack[key].index += 1;
            }
        }
        return _redoValue;
    };

    /**
     * Store current anchor position within given node
     */
    this.storeSelection = function storeSelection() {
        vm.stopEvents = true;
        vm.selection = window.rangy ? window.rangy.saveSelection() : null;
    };

    /**
     * Reset stored anchor position in given node
     */
    this.resetSelection = function resetSelection(node) {
        if (vm.selection) {
            window.rangy.restoreSelection(vm.selection);
            vm.selection = null;
        }

        clearRangy(node);
        vm.stopEvents = false;
    };

    /**
     * Remove all rangy stored selections from given node
     *
     * @param {Node} node
     */
    function clearRangy(node) {
        var spans = node.getElementsByClassName('rangySelectionBoundary');
        while (spans.length) {
            var span = spans.item(0);
            span.parentNode.removeChild(span);
        }
    }

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
        this.command = new FindReplaceCommand(this.elem, vm);
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

    function addEventListeners(elem) {
        elem.addEventListener('blur', stopEventListener);
        elem.addEventListener('input', stopEventListener);
        elem.addEventListener('focus', stopEventListener);
        elem.addEventListener('select', stopEventListener);
        document.body.addEventListener('focus', stopEventListener, true);
    }

    function removeEventListeners(elem) {
        elem.removeEventListener('blur', stopEventListener);
        elem.removeEventListener('input', stopEventListener);
        elem.removeEventListener('focus', stopEventListener);
        elem.removeEventListener('select', stopEventListener);
        document.body.removeEventListener('focus', stopEventListener);
    }

    function stopEventListener(event) {
        if (vm.stopEvents) {
            event.stopImmediatePropagation();
            event.stopPropagation();
        }
    }
}

function FindReplaceCommand(rootNode, _editor) {
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
        if (node.nodeType === Node.TEXT_NODE) {
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
                    html = angular.element(rootNode).html();
                    _editor.savetoHistory('bodyhtml', html);
                    _editor.triggerModelUpdate();
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
            disablePlaceholders: true,
            spellcheck: false
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
                if (p.childNodes.length && p.childNodes[0].nodeType === Node.TEXT_NODE) {
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
            if (selection.anchorNode.nodeType === Node.TEXT_NODE) {
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
            scope: {type: '=', config: '=', language: '='},
            require: 'ngModel',
            templateUrl: 'scripts/superdesk/editor/views/editor.html',
            link: function(scope, elem, attrs, ngModel) {

                var editorElem,
                    updateTimeout,
                    renderTimeout;

                editor.resetStack(elem[0].id);

                ngModel.$viewChangeListeners.push(changeListener);
                scope.viewvalue = ngModel.$viewValue;

                ngModel.$render = function renderEditor() {
                    spellcheck.setLanguage(scope.language);

                    editorElem = elem.find(scope.type === 'preformatted' ?  '.editor-type-text' : '.editor-type-html');

                    editorElem.empty();
                    editorElem.html(ngModel.$viewValue || '');

                    var initialValue = ngModel.$viewValue != null ? ngModel.$viewValue : '';
                    editor.setInitialValue(elem[0].id, initialValue);

                    editor.elem = editorElem[0];
                    editor.addEventListeners(editorElem[0]);

                    var editorConfig = angular.extend({}, config, scope.config || {});
                    editor.editor = new window.MediumEditor(editor.elem, editorConfig);

                    editorElem.on('input blur', function(event) {
                        $timeout.cancel(updateTimeout);
                        updateTimeout = $timeout(function() { updateModel(event); }, 500, false);
                    });
                    editorElem.on('keyup', function(event) {
                        if (event.ctrlKey) {
                            if (event.keyCode === editor.KEY_CODES.X) {
                                doUndo();
                            } else if (event.keyCode === editor.KEY_CODES.Y) {
                                doRedo();
                            }
                        }
                    });
                    editorElem.on('contextmenu', function(event) {
                        if (spellcheck.isErrorNode(event.target)) {
                            event.preventDefault();
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
                        editor.clear();
                        editor.removeEventListeners(editorElem[0]);
                        editorElem.off();
                        spellcheck.setLanguage(null);
                    });

                    scope.cursor = {};
                    autoRenderSpellcheck();
                };

                scope.replace = function(text) {
                    scope.replaceTarget.parentNode.replaceChild(document.createTextNode(text), scope.replaceTarget);
                };

                scope.addWordToDictionary = function() {
                    var word = scope.replaceTarget.textContent;
                    spellcheck.addWordToUserDictionary(word);
                };

                scope.$on('editor:settings', function() {
                    if (editor.settings.spellcheck) {
                        renderSpellcheck();
                    } else {
                        removeSpellcheck(editorElem[0]);
                    }
                });

                scope.$on('spellcheck:run', renderSpellcheck);
                scope.$on('key:ctrl:shift:s', renderSpellcheck);

                function doUndo() {
                    scope.$applyAsync(function() {
                        var viewValue = editor.getUndoViewValue(elem[0].id);
                        ngModel.$setViewValue(viewValue);
                        editorElem.html(ngModel.$modelValue);
                    });
                }

                function doRedo() {
                    scope.$applyAsync(function() {
                        var viewValue = editor.getRedoViewValue(elem[0].id);
                        ngModel.$setViewValue(viewValue);
                        editorElem.html(ngModel.$modelValue);
                    });
                }

                function updateModel(event) {
                    if (editor.readOnly) {
                        return;
                    }

                    var html = removeSpellcheck(editorElem[0]);
                    var key = elem[0].id;
                    // get model value in text
                    var div = document.createElement('div');
                    div.innerHTML = ngModel.$viewValue != null ? ngModel.$viewValue : '';
                    var modelTextValue = div.textContent || div.innerText || '';
                    // Compare model changes and apply
                    if (event.type === 'input' && !_.isEqual(event.currentTarget.textContent.trim(), '')) {
                        if (editor.fieldStack[key] != null) {
                            if (!_.isEqual(event.currentTarget.innerHTML,
                                editor.fieldStack[key].stack[editor.fieldStack[key].stack.length - 1])) {
                                if (!_.isEqual(event.currentTarget.textContent.trim(), modelTextValue.trim())) {
                                    // Invalidate items higher on the stack, if we are here after having undo called.
                                    editor.fieldStack[key].stack.splice(editor.fieldStack[key].index + 1,
                                        editor.fieldStack[key].stack.length - editor.fieldStack[key].index);
                                    editor.fieldStack[key].stack.push(html);
                                    editor.fieldStack[key].index = editor.fieldStack[key].stack.length - 1;
                                    scope.$applyAsync(function() {
                                        ngModel.$setViewValue(html);
                                    });
                                }
                            }
                        }
                    }
                }

                function changeListener() {
                    $timeout.cancel(renderTimeout);
                    renderTimeout = $timeout(autoRenderSpellcheck, 200, false);
                }

                function autoRenderSpellcheck() {
                    if (editor.settings.spellcheck) {
                        renderSpellcheck();
                    }
                }

                function renderSpellcheck() {
                    spellcheck.render(editorElem[0]);
                }

                function removeSpellcheck(node) {
                    var html;

                    if (!node) {
                        node = editorElem[0];
                    }

                    editor.storeSelection(node);
                    html = spellcheck.clean(node);
                    html = html.replace('\ufeff', ''); // remove rangy marker
                    node.innerHTML = html; // remove rangy marker
                    editor.resetSelection(node);
                    return html;
                }
            }
        };
    }]);

})();
