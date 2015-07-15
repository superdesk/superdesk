
/**
 * Spellcheck module
 */
(function() {

'use strict';

var ERROR_CLASS = 'sderror';

/**
 * Find text node + offset for given node and offset
 */
function findTextNode(node, offset) {
    var currentOffset = 0,
        tree = document.createTreeWalker(node, NodeFilter.SHOW_TEXT);
    while (tree.nextNode()) {
        if (currentOffset + tree.currentNode.textContent.length >= offset) {
            return {node: tree.currentNode, offset: offset - currentOffset};
        }

        currentOffset += tree.currentNode.length;
    }
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
    var lang,
        dict,
        numberOfErrors,
        COLOR = '#123456', // use some unlikely color for hilite, we will change these to class
        COLOR_RGB = rgb(COLOR);

    /**
     * Set current language
     *
     * @param {string} _lang
     */
    this.setLanguage = function(_lang) {
        if (lang !== _lang) {
            lang = _lang;
            dict = null;
        }
    };

    /**
     * Test if given elem is an error
     */
    this.isErrorNode = function(elem) {
        return elem.classList.contains(ERROR_CLASS);
    };

    /**
     * Get dictionary for spellchecking
     *
     * @return {Promise}
     */
    function getDict() {
        if (!lang) {
            return $q.reject();
        }

        if (!dict) {
            dict = dictionaries.getActive(lang).then(function(items) {
                dict.content = {};
                angular.forEach(items, addDict);
                return dict.content;
            });
        }

        return dict;
    }

    /**
     * Add dictionary content to spellcheck
     *
     * @param {Object} item
     */
    function addDict(item) {
        angular.extend(dict.content, item.content || {});
    }

    /**
     * Find errors in given text
     *
     * @param {string} text
     */
    this.errors = function check(text) {
        return getDict().then(function(d) {
            var errors = [],
                regexp = /[0-9a-zA-Z\u00C0-\u1FFF\u2C00-\uD7FF]+/g,
                match;
            while ((match = regexp.exec(text)) != null) {
                var word = match[0];
                if (isNaN(word) && !dict.content[word.toLowerCase()]) {
                    errors.push({
                        word: word,
                        index: match.index
                    });
                }
            }

            numberOfErrors = errors.length;
            return errors;
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
        var selection = document.getSelection(),
            range = document.createRange(),
            start = findTextNode(node, error.index),
            end = findTextNode(node, error.index + error.word.length);
        if (start.node === end.node) {
            // optimize error hilite when the word is within single text node
            var replace = start.node.splitText(start.offset),
                span = document.createElement('span');
            span.classList.add(ERROR_CLASS);
            replace.splitText(end.offset - start.offset);
            span.textContent = replace.textContent;
            replace.parentNode.replaceChild(span, replace);
        } else {
            range.setStart(start.node, start.offset);
            range.setEnd(end.node, end.offset);
            selection.removeAllRanges();
            selection.addRange(range);
            document.execCommand('hiliteColor', false, COLOR);
        }
    }

    /**
     * Highlite words in given elem that are not in dict
     *
     * @param {Node} elem
     */
    this.render = function render(elem) {
        var node = elem;

        return this.errors(node.textContent)
            .then(function(errors) {
                editor.storeSelection(node);

                angular.forEach(errors, function(error) {
                    hiliteError(node, error);
                });

                setErrorClass(node);
                editor.resetSelection(node);
            });
    };

    /**
     * Return number of spelling errors
     */
    this.countErrors = function() {
        return numberOfErrors;
    };

    /**
     * Remove highliting from given elem
     */
    this.clean = function(elem) {
        return removeClass(elem, ERROR_CLASS);
    };

    /**
     * Get suggested corrections for given word
     *
     * @param {string} word
     */
    this.suggest = function suggest(word) {
        return api.save('spellcheck', {
            word: word,
            language_id: lang
        }).then(function(result) {
            return result.corrections || [];
        });
    };

    /**
     * Add word to user dictionary
     */
    this.addWordToUserDictionary = function(word) {
        dictionaries.addWordToUserDictionary(word, lang);
        dict.content[word] = dict.content[word] ? dict.content[word] + 1 : 1;
    };
}

SpellcheckMenuController.$inject = ['editor', '$rootScope'];
function SpellcheckMenuController(editor, $rootScope) {
    this.isAuto = editor.settings.spellcheck || true;
    this.spellcheck = spellcheck;
    this.pushSettings = pushSettings;

    var vm = this;

    function spellcheck() {
        $rootScope.$broadcast('spellcheck:run');
    }

    function pushSettings() {
        editor.settings = angular.extend({}, editor.settings, {spellcheck: vm.isAuto});
        $rootScope.$broadcast('editor:settings', {spellcheck: vm.isAuto});
    }
}

angular.module('superdesk.editor.spellcheck', ['superdesk.dictionaries', 'superdesk.editor'])
    .service('spellcheck', SpellcheckService)
    .controller('SpellcheckMenu', SpellcheckMenuController)
    ;

})();
