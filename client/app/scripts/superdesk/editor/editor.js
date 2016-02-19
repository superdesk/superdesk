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

/**
 * Generate click event on given target node
 *
 * @param {Node} target
 */
function click(target) {
    target.dispatchEvent(new MouseEvent('click'));
}

/**
 * Replace given dom elem with its contents
 *
 * It is like jQuery unwrap
 *
 * @param {Node} elem
 */
function replaceSpan(elem) {
    var parent = elem.parentNode;
    while (elem.hasChildNodes()) {
        parent.insertBefore(elem.childNodes.item(0), elem);
    }

    parent.removeChild(elem);
}

/**
 * Remove all elements with given className but keep its contents
 *
 * @param {Node} elem
 * @param {string} className
 * @return {Node}
 */
function removeClass(elem, className) {
    var node = elem.cloneNode(true);
    var spans = node.getElementsByClassName(className);
    while (spans.length) {
        replaceSpan(spans.item(0));
    }

    node.normalize();
    return node;
}

/**
 * Find text node + offset for given node and offset
 *
 * This will find text node within given node that contains character on given offset
 *
 * @param {Node} node
 * @param {numeric} offset
 * @return {Object} {node: {Node}, offset: {numeric}}
 */
function findTextNode(node, offset) {
    var tree = document.createTreeWalker(node, NodeFilter.SHOW_TEXT);
    var currentLength;
    var currentOffset = 0;
    var ZERO_WIDTH_SPACE = String.fromCharCode(65279);
    while (tree.nextNode()) {
        tree.currentNode.textContent = tree.currentNode.textContent.replace(ZERO_WIDTH_SPACE, '');
        currentLength = tree.currentNode.textContent.length;
        if (currentOffset + currentLength >= offset) {
            return {node: tree.currentNode, offset: offset - currentOffset};
        }

        currentOffset += currentLength;
    }
}

/**
 * History stack
 *
 * It supports undo/redo operations
 *
 * @param {string} initialValue
 */
function HistoryStack(initialValue) {
    var stack = [];
    var index = -1;

    /**
     * Add a new value to stack and remove all furhter redo values
     * so after manual change there is no way to redo.
     *
     * @param {string} value
     */
    this.add = function(value) {
        index = index + 1;
        stack[index] = value;
        stack.splice(index + 1, stack.length);
    };

    /**
     * Select previous value (undo)
     */
    this.selectPrev = function() {
        index = Math.max(-1, index - 1);
    };

    /**
     * Select next value (redo)
     */
    this.selectNext = function() {
        index = stack[index + 1] != null ? index + 1 : index;
    };

    /**
     * Get current value
     */
    this.get = function() {
        var state = index > -1 ? stack[index] : initialValue;
        return state;
    };
}

EditorService.$inject = ['spellcheck', '$rootScope', '$timeout'];
function EditorService(spellcheck, $rootScope, $timeout) {
    this.settings = {spellcheck: true};

    this.KEY_CODES = Object.freeze({
        Y: 'Y'.charCodeAt(0),
        Z: 'Z'.charCodeAt(0)
    });

    this.ARROWS = Object.freeze({
        33: 1, // page up
        34: 1, // page down
        35: 1, // end
        36: 1, // home
        37: 1, // left
        38: 1, // up
        39: 1, // right
        40: 1  // down
    });

    this.META = Object.freeze({
        16: 1, // shift
        17: 1, // ctrl
        18: 1, // alt
        20: 1, // caps lock
        91: 1, // left meta in webkit
        93: 1, // right meta in webkit
        224: 1 // meta in firefox
    });

    /**
     * Test if given keyboard event should be ignored as it's not changing content.
     *
     * @param {Event} event
     * @return {boolen}
     */
    this.shouldIgnore = function (event) {
        // ignore arrows
        if (self.ARROWS[event.keyCode]) {
            return true;
        }

        // ignore meta keys (ctrl, shift or meta only)
        if (self.META[event.keyCode]) {
            return true;
        }

        // ignore shift + ctrl/meta + something
        if (event.shiftKey && (event.ctrlKey || event.metaKey)) {
            return true;
        }

        return false;
    };

    var ERROR_CLASS = 'sderror';
    var HILITE_CLASS = 'sdhilite';
    var ACTIVE_CLASS = 'sdactive';
    var FINDREPLACE_CLASS = 'sdfindreplace';

    var self = this;
    var scopes = [];

    /**
     * Register given scope - it adds history stack to it and keeps reference
     *
     * @param {Scope} scope
     */
    this.registerScope = function(scope) {
        scopes.push(scope);
        scope.history = new HistoryStack(scope.model.$viewValue || '');
        scope.$on('$destroy', function() {
            var index = scopes.indexOf(scope);
            scopes.splice(index, 1);
        });
    };

    /**
     * Remove highlighting from given scope and return its contents
     *
     * @param {Scope} scope
     * @return {string}
     */
    this.cleanScope = function(scope) {
        self.storeSelection(scope.node);
        var html = clean(scope.node).innerHTML;
        html = html.replace('\ufeff', ''); // remove rangy marker
        scope.node.innerHTML = html;
        self.resetSelection(scope.node);
        return html;
    };

    /**
     * Render highlights for given scope based on settings
     *
     * @param {Scope} scope
     * @param {Scope} force force rendering manually - eg. via keyboard
     */
    this.renderScope = function(scope, force, preventStore) {
        self.cleanScope(scope);
        if (self.settings.findreplace) {
            renderFindreplace(scope.node);
        } else if (self.settings.spellcheck || force) {
            renderSpellcheck(scope.node, preventStore);
        }
    };

    /**
     * Render highlights in all registered scopes
     */
    this.render = function() {
        scopes.forEach(self.renderScope);
    };

    /**
     * Remove highlight markup from given node
     *
     * @param {Node} node
     * @return {Node}
     */
    function clean(node) {
        return removeClass(node, HILITE_CLASS);
    }

    /**
     * Highlight find&replace matches in given node
     *
     * @param {Node} node
     */
    function renderFindreplace(node) {
        var tokens = getFindReplaceTokens(node);
        hilite(node, tokens, FINDREPLACE_CLASS);
    }

    /**
     * Find all matches for current find&replace needle in given node
     *
     * Each match is {word: {string}, offset: {number}} in given node,
     * we can't return nodes here because those will change when we start
     * highlighting and offsets wouldn't match
     *
     * @param {Node} node
     * @return {Array} list of matches
     */
    function getFindReplaceTokens(node) {
        var tokens = [];
        var needle = self.settings.findreplace.needle || null;

        if (!needle) {
            return tokens;
        }

        var tree = document.createTreeWalker(node, NodeFilter.SHOW_TEXT);
        var currentOffset = 0;
        var index, text;
        while (tree.nextNode()) {
            text = tree.currentNode.textContent;
            while ((index = text.indexOf(needle)) > -1) {
                tokens.push({
                    word: text.substr(index, needle.length),
                    index: currentOffset + index
                });

                text = text.substr(index + needle.length);
                currentOffset += index + needle.length;
            }

            currentOffset += text.length;
        }

        return tokens;
    }

    /**
     * Highlight spellcheck errors in given node
     *
     * @param {Node} node
     */
    function renderSpellcheck(node, preventStore) {
        spellcheck.errors(node).then(function(tokens) {
            hilite(node, tokens, ERROR_CLASS, preventStore);
        });
    }

    /**
     * Hilite all tokens within node using span with given className
     *
     * This first stores caret position, updates markup, and then restores the caret.
     *
     * @param {Node} node
     * @param {Array} tokens
     * @param {string} className
     * @param {Boolean} preventStore
     */
    function hilite(node, tokens, className, preventStore) {
        if (!tokens.length) {
            self.resetSelection(node);
            return;
        }

        if (!preventStore) {
            self.storeSelection(node);
        }
        var token = tokens.shift();
        hiliteToken(node, token, className);
        $timeout(function() {
            hilite(node, tokens, className, true);
        }, 0, false);
    }

    /**
     * Highlight single `token` via putting it into a span with given class
     *
     * @param {Node} node
     * @param {Object} token
     * @param {string} className
     */
    function hiliteToken(node, token, className) {
        var start = findTextNode(node, token.index);
        var end = findTextNode(node, token.index + token.word.length);

        // correction for linebreaks - first node on a new line is set to
        // linebreak text node which is not even visible in dom, maybe dom bug?
        if (start.node !== end.node) {
            start.node = end.node;
            start.offset = 0;
        }

        var replace = start.node.splitText(start.offset);
        var span = document.createElement('span');
        span.classList.add(className);
        span.classList.add(HILITE_CLASS);
        replace.splitText(end.offset - start.offset);
        span.textContent = replace.textContent;
        replace.parentNode.replaceChild(span, replace);
    }

    /**
     * Set next highlighted node active.
     *
     * In case there is no node selected select first one.
     */
    this.selectNext = function() {
        var nodes = document.body.getElementsByClassName(HILITE_CLASS);
        for (var i = 0; i < nodes.length; i++) {
            var node = nodes.item(i);
            if (node.classList.contains(ACTIVE_CLASS)) {
                node.classList.remove(ACTIVE_CLASS);
                nodes.item((i + 1) % nodes.length).classList.add(ACTIVE_CLASS);
                return;
            }
        }

        if (nodes.length) {
            nodes.item(0).classList.add(ACTIVE_CLASS);
        }
    };

    /**
     * Set previous highlighted node active.
     */
    this.selectPrev = function() {
        var nodes = document.body.getElementsByClassName(HILITE_CLASS);
        for (var i = 0; i < nodes.length; i++) {
            var node = nodes.item(i);
            if (node.classList.contains(ACTIVE_CLASS)) {
                node.classList.remove(ACTIVE_CLASS);
                nodes.item(i === 0 ? nodes.length - 1 : i - 1).classList.add(ACTIVE_CLASS);
                return;
            }
        }
    };

    /**
     * Replace active node with given text.
     *
     * @param {string} text
     */
    this.replace = function(text) {
        scopes.forEach(function(scope) {
            var nodes = scope.node.getElementsByClassName(ACTIVE_CLASS);
            replaceNodes(nodes, text, scope);
            self.commitScope(scope);
        });
    };

    /**
     * Replace all highlighted nodes with given text.
     *
     * @param {string} text
     */
    this.replaceAll = function(text) {
        scopes.forEach(function(scope) {
            var nodes = scope.node.getElementsByClassName(HILITE_CLASS);
            replaceNodes(nodes, text);
            self.commitScope(scope);
        });
    };

    /**
     * Replace all nodes with text
     *
     * @param {HTMLCollection} nodes
     * @param {string} text
     */
    function replaceNodes(nodes, text) {
        while (nodes.length) {
            var node = nodes.item(0);
            var textNode = document.createTextNode(text);
            node.parentNode.replaceChild(textNode, node);
            textNode.parentNode.normalize();
        }
    }

    /**
     * Store current anchor position within given node
     */
    this.storeSelection = function storeSelection() {
        self.selection = window.rangy ? window.rangy.saveSelection() : null;
    };

    /**
     * Reset stored anchor position in given node
     */
    this.resetSelection = function resetSelection(node) {
        if (self.selection) {
            window.rangy.restoreSelection(self.selection);
            self.selection = null;
        }

        clearRangy(node);
    };

    /**
     * Remove all rangy stored selections from given node
     *
     * @param {Node} node
     * @return {Node}
     */
    function clearRangy(node) {
        var spans = node.getElementsByClassName('rangySelectionBoundary');
        while (spans.length) {
            var span = spans.item(0);
            span.parentNode.removeChild(span);
            if (span.parentNode.normalize) {
                span.parentNode.normalize();
            }
        }

        return node;
    }

    /**
     * Update settings
     *
     * @param {Object} settings
     */
    this.setSettings = function(settings) {
        self.settings = angular.extend({}, self.settings, settings);
    };

    /**
     * Test if given elem is a spellcheck error node
     *
     * @param {Node} elem
     * @return {boolean}
     */
    this.isErrorNode = function(elem) {
        return elem.classList.contains(ERROR_CLASS);
    };

    /**
     * Commit changes in all scopes
     */
    this.commit = function() {
        scopes.forEach(self.commitScope);
    };

    /**
     * Commit changes in given scope to its model
     *
     * @param {Scope} scope
     */
    this.commitScope = function(scope) {
        var nodeValue = clearRangy(clean(scope.node)).innerHTML;
        if (nodeValue !== scope.model.$viewValue) {
            scope.model.$setViewValue(nodeValue);
            scope.history.add(scope.model.$viewValue);
        }
    };

    /**
     * Undo last operation
     *
     * @param {Scope} scope
     */
    this.undo = function(scope) {
        scope.history.selectPrev();
        useHistory(scope);
    };

    /**
     * Redo previous operation
     *
     * @param {Scope} scope
     */
    this.redo = function(scope) {
        scope.history.selectNext();
        useHistory(scope);
    };

    /**
     * Use value from history and set it as node/model value.
     *
     * @param {Scope} scope
     */
    function useHistory(scope) {
        var val = scope.history.get();
        if (val != null) {
            scope.node.innerHTML = val;
            scope.model.$setViewValue(val);
        }
    }
}

SdTextEditorBlockEmbedController.$inject = ['$timeout', '$element', '$scope'];
function SdTextEditorBlockEmbedController($timeout, $element, $scope) {
    var vm = this;
    angular.extend(vm, {
        embedCode: undefined,  // defined below
        caption: undefined,  // defined below
        editable: false,
        toggleEdition: function() {
            vm.editable = !vm.editable;
        },
        updateEmbedPreview: function() {
            angular.element($element).find('.preview--embed').html(vm.model.body);
        },
        // in edition
        save: function() {
            // update the block's model
            angular.extend(vm.model, {
                body: vm.embedCode,
                caption: vm.caption
            });
            vm.updateEmbedPreview();
            // on change callback
            vm.onBlockChange();
        },
        cancel: function() {
            vm.embedCode = vm.model.body;
            vm.caption = vm.model.caption;
        }
    });
    $timeout(function() {
        vm.updateEmbedPreview();
        vm.embedCode = vm.model.body;
        vm.caption = vm.model.caption;
    });
}

angular.module('superdesk.editor', ['superdesk.editor.spellcheck', 'angular-embed',
                                    'superdesk.config'])
    .service('editor', EditorService)
    .constant('EMBED_PROVIDERS', { // see http://noembed.com/#supported-sites
        custom: 'Custom',
        twitter: 'Twitter',
        youtube: 'YouTube'
    })
    .directive('sdAddEmbed', ['$timeout', function($timeout) {
        return {
            scope: {addToPosition: '=', extended: '=', onClose: '&'},
            require: ['sdAddEmbed', '^sdTextEditor'],
            templateUrl: 'scripts/superdesk/editor/views/add-embed.html',
            controllerAs: 'vm',
            controller: 'SdAddEmbedController',
            bindToController: true,
            link: function(scope, element, attrs, controllers) {
                var vm = controllers[0];
                angular.extend(vm, {
                    editorCtrl: controllers[1]
                });
                // listen to the escape touch to close the field when pressed
                element.bind('keyup', function(e) {
                    if (e.keyCode === 27) { // escape
                        $timeout(function() {
                            vm.extended = false;
                        });
                    }
                });
            }
        };
    }])
    .directive('sdTextEditorDropZone', ['superdesk', 'api', function (superdesk, api) {
        return {
            scope: true,
            require: '^sdAddEmbed',
            link: function(scope, element, attrs, ctrl) {
                var PICTURE_TYPE = 'application/superdesk.item.picture';
                element
                .on('drop', function(event) {
                    event.preventDefault();
                    var item = angular.fromJson(event.originalEvent.dataTransfer.getData(PICTURE_TYPE));
                    superdesk.intent('edit', 'crop', {item: item, renditions: [{name: 'embed'}]})
                        .then(function(cropData) {
                            return api.save('picture_crop', {item: item, crop: cropData.embed});
                        })
                        .then(function(image) {
                            ctrl.createBlockFromSdPicture(image, item);
                        }).finally(function() {
                            element.removeClass('drag-active');
                        });
                })
                .on('dragover', function(event) {
                    if (event.originalEvent.dataTransfer.types[0] === PICTURE_TYPE) {
                        event.preventDefault();
                        element.addClass('drag-active');
                    }
                })
                .on('dragleave', function(event) {
                    element.removeClass('drag-active');
                });
            }
        };
    }])
    .directive('sdTextEditor', ['$timeout', function ($timeout) {
        return {
            scope: {type: '=', config: '=', language: '='},
            require: ['sdTextEditor', 'ngModel'],
            templateUrl: 'scripts/superdesk/editor/views/editor.html',
            controllerAs: 'vm',
            controller: 'SdTextEditorController',
            bindToController: true,
            link: function(scope, element, attr, controllers) {
                var controller = controllers[0];
                var ngModel = controllers[1];
                $timeout(function() {
                    if (controller.config.multiBlockEdition) {
                        controller.initEditorWithMultipleBlock(ngModel);
                    } else {
                        controller.initEditorWithOneBlock(ngModel);
                    }
                });
            }
        };
    }])
    .directive('sdTextEditorBlockEmbed', ['$timeout', function ($timeout) {
        return {
            scope: {type: '=', config: '=', language: '=', model: '=sdTextEditorBlockEmbed', onBlockChange: '&'},
            templateUrl: 'scripts/superdesk/editor/views/block-embed.html',
            controllerAs: 'vm',
            bindToController: true,
            controller: SdTextEditorBlockEmbedController
        };
    }])
    .directive('sdTextEditorBlockText', ['editor', 'spellcheck', '$timeout', 'superdesk',
    function (editor, spellcheck, $timeout, superdesk) {
        var EDITOR_CONFIG = {
            toolbar: {
                static: true,
                align: 'left',
                sticky: true,
                stickyTopOffset: 96, // header height
                updateOnEmptySelection: true,
                buttons: [
                    // H1 and H2 buttons which actually produce
                    // <h2> and <h3> tags respectively
                    {
                        name: 'h1',
                        action: 'append-h2',
                        aria: 'header type 1',
                        tagNames: ['h2'],
                        contentDefault: '<b>H1</b>',
                        classList: ['custom-class-h1'],
                        attrs: {
                            'data-custom-attr': 'attr-value-h1'
                        }
                    },
                    {
                        name: 'h2',
                        action: 'append-h3',
                        aria: 'header type 2',
                        tagNames: ['h3'],
                        contentDefault: '<b>H2</b>',
                        classList: ['custom-class-h2'],
                        attrs: {
                            'data-custom-attr': 'attr-value-h2'
                        }
                    },
                    'bold', 'italic', 'underline', 'quote', 'anchor'
                ]
            },
            anchor: {
                placeholderText: gettext('Paste or type a full link')
            },
            placeholder: false,
            disableReturn: false,
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

        function extractBlockContentsFromCaret() {
            function getBlockContainer(node) {
                while (node) {
                    if (node.nodeType === 1 && /^(DIV)$/i.test(node.nodeName)) {
                        return node;
                    }
                    node = node.parentNode;
                }
            }
            var sel = window.getSelection();
            if (sel.rangeCount) {
                var selRange = sel.getRangeAt(0);
                var blockEl = getBlockContainer(selRange.endContainer);
                if (blockEl) {
                    var range = selRange.cloneRange();
                    range.selectNodeContents(blockEl);
                    range.setStart(selRange.endContainer, selRange.endOffset);
                    var remaining = range.extractContents();
                    // remove empty last line
                    $(blockEl).find('p:last').each(function() {
                        if ($(this).text() === '') {
                            this.remove();
                        }
                    });
                    return remaining;
                }
            }
        }

        return {
            scope: {type: '=', config: '=', language: '=', sdTextEditorBlockText: '='},
            require: ['ngModel', '^sdTextEditor'],
            templateUrl: 'scripts/superdesk/editor/views/block-text.html',
            link: function(scope, elem, attrs, controllers) {
                var ngModel = controllers[0];
                var sdTextEditor = controllers[1];
                scope.model = ngModel;
                var TYPING_CLASS = 'typing';
                var editorElem;
                var updateTimeout;
                var renderTimeout;
                ngModel.$viewChangeListeners.push(changeListener);
                ngModel.$render = function() {
                    editor.registerScope(scope);
                    var editorConfig = angular.extend({}, EDITOR_CONFIG, scope.config || {});
                    // if config.multiBlockEdition is true, add Embed and Image button to the toolbar
                    if (scope.config.multiBlockEdition) {
                        var EmbedButton = window.MediumEditor.extensions.button.extend({
                            name: 'embed',
                            contentDefault: '<b>Embed</b>', // default innerHTML of the button
                            init: function() {
                                window.MediumEditor.extensions.form.prototype.init.apply(this, arguments);
                                this.subscribe('editableKeydown', this.handleKeydown.bind(this));
                            },
                            isAlreadyApplied: function (node) {
                                var textContent = angular.isDefined(node.textContent) ? node.textContent : node.innerText;
                                return ['p', 'div'].indexOf(node.nodeName.toLowerCase()) > -1 && textContent === '';
                            },
                            isActive: function() {
                                return !this.button.classList.contains('medium-editor-button-disabled');
                            },
                            setInactive: function() {
                                this.button.classList.add('medium-editor-button-disabled');
                            },
                            setActive: function() {
                                this.button.classList.remove('medium-editor-button-disabled');
                            },
                            extractEndOfBlock: function() {
                                // save caret position
                                scope.sdTextEditorBlockText.caretPosition = this.base.exportSelection();
                                // extract the text after the cursor
                                var remainingElementsContainer = document.createElement('div');
                                remainingElementsContainer.appendChild(extractBlockContentsFromCaret().cloneNode(true));
                                // remove the first line if empty
                                $(remainingElementsContainer).find('p:first').each(function() {
                                    if ($(this).text() === '') {
                                        this.remove();
                                    }
                                });
                                return remainingElementsContainer;
                            },
                            handleClick: function() {
                                // does nothing if embed must be inactive
                                if (!this.isActive()) {
                                    return false;
                                }
                                var indexWhereToAddNewBlock = sdTextEditor.getBlockPosition(scope.sdTextEditorBlockText) + 1;
                                var remainingText = this.extractEndOfBlock().innerHTML;
                                // save the blocks (with removed leading text)
                                updateModel();
                                // add new text block for the remaining text
                                sdTextEditor.insertNewBlock(indexWhereToAddNewBlock, {
                                    body: remainingText
                                }, true);
                                // hide the toolbar
                                this.base.getExtensionByName('toolbar').hideToolbarDefaultActions();
                                // show the add-embed form
                                scope.sdTextEditorBlockText.showAndFocusLowerAddAnEmbedBox();
                            },
                            // Called when user hits the defined shortcut (CTRL / COMMAND + e)
                            handleKeydown: function(event) {
                                if (window.MediumEditor.util.isKey(event, 'E'.charCodeAt(0)) &&
                                    window.MediumEditor.util.isMetaCtrlKey(event) && !event.shiftKey) {
                                    this.handleClick(event);
                                    event.preventDefault();
                                }
                            }
                        });
                        var PictureButton = EmbedButton.extend({
                            name: 'picture',
                            contentDefault: '<b>Picture</b>', // default innerHTML of the button
                            init: function() {
                                window.MediumEditor.extensions.form.prototype.init.apply(this, arguments);
                            },
                            handleClick: function() {
                                var self = this;
                                // does nothing if inactive
                                if (!self.isActive()) {
                                    return false;
                                }
                                // extract text after cursor
                                var textAfterCursor = self.extractEndOfBlock().innerHTML;
                                // save the blocks (with removed leading text)
                                updateModel();
                                var indexWhereToAddBlock = sdTextEditor.getBlockPosition(scope.sdTextEditorBlockText) + 1;
                                superdesk.intent('upload', 'media').then(function(images) {
                                    images.forEach(function(image) {
                                        sdTextEditor.insertNewBlock(indexWhereToAddBlock, {
                                            blockType: 'embed',
                                            embedType: 'Image',
                                            body: '<img alt="' + (image.description_text || '') + '" src="' +
                                                image.renditions.viewImage.href + '"/>\n',
                                            caption: image.description_text
                                        }, true);
                                        indexWhereToAddBlock++;
                                    });
                                    // add new text block for the remaining text
                                }).finally(function() {
                                    sdTextEditor.insertNewBlock(indexWhereToAddBlock, {
                                        body: textAfterCursor
                                    }, true);
                                });
                            }
                        });
                        editorConfig.toolbar.buttons.push('embed', 'picture');
                        editorConfig.extensions = {
                            'embed': new EmbedButton(),
                            'upload': new PictureButton()
                        };
                    }
                    // FIXME: create unwanted cursor moves
                    // spellcheck.setLanguage(scope.language);
                    editorElem = elem.find(scope.type === 'preformatted' ?  '.editor-type-text' : '.editor-type-html');
                    editorElem.empty();
                    editorElem.html(ngModel.$viewValue || '');
                    scope.node = editorElem[0];
                    scope.model = ngModel;
                    // destroy exiting instance
                    if (scope.medium) {
                        scope.medium.destroy();
                    }
                    // create a new instance of the medium editor binded to this node
                    scope.medium = new window.MediumEditor(scope.node, editorConfig);
                    // restore the selection if exist
                    if (scope.sdTextEditorBlockText.caretPosition) {
                        scope.node.focus();
                        scope.medium.importSelection(scope.sdTextEditorBlockText.caretPosition);
                        // clear the saved position
                        scope.sdTextEditorBlockText.caretPosition = undefined;
                    }
                    // listen updates by medium editor to update the model
                    scope.medium.subscribe('editableInput', function() {
                        cancelTimeout();
                        updateTimeout = $timeout(updateModel, 800, false);
                    });
                    // Add or remove the class toolbar-visible to the editor depending of the toolbar state
                    scope.medium.subscribe('showToolbar', function() {
                        editorElem.addClass('toolbar-visible');
                    });
                    scope.medium.subscribe('hideToolbar', function() {
                        editorElem.removeClass('toolbar-visible');
                    });
                    scope.$on('spellcheck:run', render);
                    scope.$on('key:ctrl:shift:s', render);
                    function cancelTimeout(event) {
                        $timeout.cancel(updateTimeout);
                        scope.node.classList.add(TYPING_CLASS);
                    }

                    var ctrlOperations = {};
                    ctrlOperations[editor.KEY_CODES.Z] = doUndo;
                    ctrlOperations[editor.KEY_CODES.Y] = doRedo;

                    editorElem.on('keydown', function(event) {
                        if (editor.shouldIgnore(event)) {
                            return;
                        }
                        cancelTimeout(event);
                    });

                    editorElem.on('keyup', function(event) {
                        if (editor.shouldIgnore(event)) {
                            return;
                        }
                        cancelTimeout(event);
                        if (event.ctrlKey && ctrlOperations[event.keyCode]) {
                            ctrlOperations[event.keyCode]();
                            return;
                        }
                        updateTimeout = $timeout(updateModel, 800, false);
                    });

                    editorElem.on('contextmenu', function(event) {
                        if (editor.isErrorNode(event.target)) {
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
                        scope.medium.destroy();
                        editorElem.off();
                        spellcheck.setLanguage(null);
                    });

                    scope.cursor = {};
                    render(null, null, true);
                };

                scope.removeBlock = function() {
                    sdTextEditor.removeBlock(scope.sdTextEditorBlockText);
                };

                function render($event, event, preventStore) {
                    scope.node.classList.remove(TYPING_CLASS);
                    editor.renderScope(scope, $event, preventStore);
                    if (event) {
                        event.preventDefault();
                    }
                }

                scope.replace = function(text) {
                    scope.replaceTarget.parentNode.replaceChild(document.createTextNode(text), scope.replaceTarget);
                    editor.commitScope(scope);
                };

                scope.addWordToDictionary = function() {
                    var word = scope.replaceTarget.textContent;
                    spellcheck.addWordToUserDictionary(word);
                    editor.render();
                };

                function doUndo() {
                    scope.$applyAsync(function() {
                        editor.undo(scope);
                        editor.renderScope(scope);
                    });
                }

                function doRedo() {
                    scope.$applyAsync(function() {
                        editor.redo(scope);
                        editor.renderScope(scope);
                    });
                }

                function updateModel() {
                    editor.commitScope(scope);
                }

                function changeListener() {
                    $timeout.cancel(renderTimeout);
                    renderTimeout = $timeout(render, 0, false);
                }
            }
        };
    }])
    .run(['embedService', 'iframelyService', function(embedService, iframelyService) {
        var pattern = 'https?:\/\/(?:www)\.playbuzz\.com(.*)$';
        var loader = '//snappa.embed.pressassociation.io/playbuzz.js';
        var html = [
            '<script type="text/javascript" src="$_LOADER"></script>',
            '<div class="pb_feed" data-game="$_URL" data-recommend="false" ',
            'data-game-info="false" data-comments="false" data-shares="false" ></div>'
        ].join('');
        embedService.registerHandler({
            name: 'PlayBuzz',
            patterns: [pattern],
            embed: function(url) {
                return iframelyService.embed(url)
                    .then(function(result) {
                        result.html = html
                            .replace('$_LOADER', loader)
                            .replace('$_URL', url.match(pattern)[1]);
                        return result;
                    });
            }
        });
    }])
    .config(['embedServiceProvider', 'iframelyServiceProvider', '$injector',
        function(embedServiceProvider, iframelyServiceProvider, $injector) {
        var config = $injector.get('config');
        // iframe.ly private key
        iframelyServiceProvider.setKey(config.iframely.key);
        // don't use noembed as first choice
        embedServiceProvider.setConfig('useOnlyFallback', true);
        // iframely respect the original embed for more services than 'embedly'
        embedServiceProvider.setConfig('fallbackService', 'iframely');
    }]);

})();
