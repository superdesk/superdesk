
/**
 * Spellcheck module
 */
(function() {

'use strict';

var ERROR_CLASS = 'sderror';

/**
 * Escape given string for usage in regexp (&copy; mdn)
 */
function escapeRegExp(string) {
    return string.replace(/[.*+?^${}()|[\]\\]/g, '\\$&');
}

/**
 * Reset cursor to first character in given node
 */
function cursorReset(node) {
    var selection = document.getSelection();
    selection.collapse(node, 0);
}

/**
 * Move cursor to given offset in given node
 */
function cursorMove(node, offset, extend) {
    var selection = document.getSelection(),
        currentOffset = 0,
        tree = document.createTreeWalker(node, NodeFilter.SHOW_TEXT);
    while (tree.nextNode()) {
        if (currentOffset + tree.currentNode.textContent.length >= offset) {
            var method = extend ? 'extend' : 'collapse';
            selection[method](tree.currentNode, offset - currentOffset);
            return;
        }

        currentOffset += tree.currentNode.length;
    }
}

/**
 * Extend selection to given offset in given node
 */
function cursorExtend(node, offset) {
    cursorMove(node, offset, true);
}

/**
 * Get rgb representation for given 'hex' color which can be compared with dom colors
 */
function rgb(color) {
    var elem = document.createElement('span');
    elem.style.color = color;
    return elem.style.color;
}

/**
 * Replace given dom elem with its contents
 */
function replaceSpan(elem) {
    var parent = elem.parentNode;
    while (elem.hasChildNodes()) {
        parent.insertBefore(elem.childNodes.item(0), elem);
    }

    parent.removeChild(elem);
    parent.normalize();
}

/**
 * Remove all elements with given className
 */
function removeClass(elem, className) {
    var node = elem.cloneNode(true),
        spans = node.getElementsByClassName(className);
    while (spans.length) {
        replaceSpan(spans.item(0));
    }

    node.normalize();
    return node.innerHTML;
}

SpellcheckService.$inject = ['$q', 'api', 'dictionaries', 'editor'];
function SpellcheckService($q, api, dictionaries, editor) {

    var dict,
        dictPromise,
        dictId,
        isRendering,
        COLOR = '#123456', // use some unlikely color for hilite, we will change these to class
        COLOR_RGB = rgb(COLOR);

    /**
     * Test if given elem is an error
     */
    this.isErrorNode = function(elem) {
        return elem.classList.contains(ERROR_CLASS);
    };

    /**
     * Get dictionary for spellchecking
     */
    function getDict() {
        if (dict) {
            return $q.when(dict);
        }

        if (!dictPromise) {
            dictPromise = dictionaries.fetch().then(function(result) {
                if (result._items.length) {
                    return dictionaries.open(result._items[0]);
                } else {
                    return $q.reject();
                }
            }).then(function(_dict) {
                dictId = _dict._id;
                dict = _dict.content;
                return dict;
            });
        }

        return dictPromise;
    }

    /**
     * Find errors in given text
     *
     * @param {string} text
     */
    this.errors = function check(text) {

        return getDict().then(function() {
            var words = text.match(/[0-9a-zA-Z\u00C0-\u1FFF\u2C00-\uD7FF]+/g),
                errors = [];
            angular.forEach(words, function(word) {
                if (isNaN(word)) {
                    var lowerWord = word.toLowerCase();
                    if (!dict[lowerWord]) {
                        errors.push(word);
                    }
                }
            });

            return _.uniq(errors);
        });
    };

    /**
     * Test if given node is error highlight
     */
    function isError(node) {
        return node.nodeName.toLowerCase() === 'span' &&
               node.style.backgroundColor === COLOR_RGB;
    }

    /**
     * Find all nodes with predefined color and set the class
     */
    function setErrorClass(node) {
        var tree = document.createTreeWalker(node, NodeFilter.SHOW_ELEMENT),
            span;
        while ((span = tree.nextNode()) != null) {
            if (isError(span)) {
                replaceStyleWithClass(span);
            }
        }
    }

    /**
     * Replace style attr with class
     */
    function replaceStyleWithClass(span) {
        span.removeAttribute('style');
        span.className = '';
        span.classList.add(ERROR_CLASS);
    }

    /**
     * Highlight `error` word in node elem
     */
    function hiliteError(node, error) {
        var regexp = new RegExp('\\b' + escapeRegExp(error) + '\\b', 'im'),
            index, lastIndex = 0, text = node.textContent;
        while ((index = text.search(regexp)) > -1) {
            cursorReset(node);
            cursorMove(node, index + lastIndex);
            cursorExtend(node, index + lastIndex + error.length);
            document.execCommand('hiliteColor', false, COLOR);
            lastIndex += index + error.length;
            text = text.substring(index + error.length);
        }
    }

    /**
     * Highlite words in given elem that are not in dict
     */
    this.render = function render(elem) {
        var node = elem;
        return this.errors(node.textContent).then(function(errors) {
            isRendering = true;
            var selection = editor.storeSelection(node);
            angular.forEach(errors, function(error) {
                hiliteError(node, error);
            });
            setErrorClass(node);
            editor.resetSelection(node, selection);
            isRendering = false;
        });
    };

    /**
     * Remove highliting from given elem
     */
    this.clean = function(elem) {
        return removeClass(elem, ERROR_CLASS);
    };

    /**
     * Get suggested corrections for given word
     */
    this.suggest = function suggest(word) {
        return api.save('spellcheck', {
            word: word,
            dict: dictId
        }).then(function(result) {
            return result.corrections || [];
        });
    };

    function preventInputEvent(event) {
        if (isRendering) {
            event.stopImmediatePropagation();
        }
    }

    this.addEventListener = function addEventListener(elem) {
        elem.addEventListener('input', preventInputEvent);
    };

    this.removeEventListener = function removeEventListener(elem) {
        elem.removeEventListener('input', preventInputEvent);
    };
}

angular.module('superdesk.editor.spellcheck', [
    'superdesk.dictionaries',
    'superdesk.editor'
    ])
    .service('spellcheck', SpellcheckService);

})();
