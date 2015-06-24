
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
        promise,
        userDict,
        dict = {},
        loaded = false,
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
            dict = {};
            userDict = null;
            loaded = false;
            promise = null;
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
     */
    function getDict() {
        if (loaded) {
            return $q.when();
        }

        if (!promise) {
            promise = dictionaries.queryByLanguage(lang)
                .then(mergeDictionaries)
                .then(fetchUserDictionary)
                .then(mergeUserDictionary);
        }

        return promise;

        function mergeDictionaries(result) {
            angular.forEach(result._items, addDict);
        }

        function fetchUserDictionary() {
            return dictionaries.getUserDictionary(lang);
        }

        function mergeUserDictionary(_userDict) {
            userDict = _userDict;
            addDict(userDict);
            loaded = true;
        }
    }

    /**
     * Add dictionary content to spellcheck
     *
     * @param {Object} item
     */
    function addDict(item) {
        angular.extend(dict, item.content || {});
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

            numberOfErrors = _.uniq(errors).length;

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
            index, lastIndex = 0, text = node.textContent,
            selection = document.getSelection();
        while ((index = text.search(regexp)) > -1) {
            var range = document.createRange(),
                start = findTextNode(node, index + lastIndex),
                end = findTextNode(node, index + lastIndex + error.length);
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

            lastIndex += index + error.length;
            text = text.substring(index + error.length);
        }
    }

    /**
     * Highlite words in given elem that are not in dict
     *
     * @param {Node} elem
     */
    this.render = function render(elem) {
        var node = elem;
        return this.errors(node.textContent).then(function(errors) {
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
        dictionaries.addWordToUserDictionary(word, userDict);
        addDict(userDict);
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
