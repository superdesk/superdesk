/**
 * Spellcheck module
 */
(function() {

'use strict';

SpellcheckService.$inject = ['$q', 'api', 'dictionaries'];
function SpellcheckService($q, api, dictionaries) {
    var lang,
        dict,
        numberOfErrors;

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
     * Find errors in given node
     *
     * @param {Node} node
     */
    this.errors = function check(node) {
        return getDict().then(function(d) {
            var errors = [],
                regexp = /[0-9a-zA-Z\u00C0-\u1FFF\u2C00-\uD7FF]+/g,
                match,
                currentOffset = 0,
                tree = document.createTreeWalker(node, NodeFilter.SHOW_TEXT);

            while (tree.nextNode()) {
                while ((match = regexp.exec(tree.currentNode.textContent)) != null) {
                    var word = match[0];
                    if (isNaN(word) && !dict.content[word.toLowerCase()]) {
                        errors.push({
                            word: word,
                            index: currentOffset + match.index
                        });
                    }
                }

                currentOffset += tree.currentNode.length;
            }

            numberOfErrors = errors.length;
            return errors;
        });
    };

    /**
     * Return number of spelling errors
     */
    this.countErrors = function() {
        return numberOfErrors;
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
        word = word.toLowerCase();
        dictionaries.addWordToUserDictionary(word, lang);
        dict.content[word] = dict.content[word] ? dict.content[word] + 1 : 1;
    };
}

SpellcheckMenuController.$inject = ['editor', '$rootScope'];
function SpellcheckMenuController(editor, $rootScope) {
    this.isAuto = editor.settings.spellcheck || true;
    this.spellcheck = spellcheck;
    this.pushSettings = pushSettings;

    var self = this;

    function spellcheck() {
        editor.setSettings({spellcheck: true});
        editor.render();
        editor.setSettings({spellcheck: false});
    }

    function pushSettings() {
        editor.setSettings({spellcheck: self.isAuto});
    }
}

angular.module('superdesk.editor.spellcheck', ['superdesk.dictionaries', 'superdesk.editor'])
    .service('spellcheck', SpellcheckService)
    .controller('SpellcheckMenu', SpellcheckMenuController)
    ;

})();
