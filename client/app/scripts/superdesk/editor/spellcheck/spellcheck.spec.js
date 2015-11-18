
'use strict';

describe('spellcheck', function() {
    var DICT = {
            what: 1,
            foo: 1,
            f1: 1,
            '3d': 1,
            is: 1,
            and: 1
        },
        USER_DICT = {
            _id: 'baz',
            user: 'foo',
            content: {
                baz: 1
            }
        },
        LANG = 'en',
        errors = [];

    beforeEach(module('superdesk.editor.spellcheck'));

    beforeEach(inject(function(dictionaries, spellcheck, $q) {

        spyOn(dictionaries, 'getActive').and.returnValue($q.when([
            {_id: 'foo', content: DICT},
            {_id: 'bar', content: {bar: 1}},
            USER_DICT
        ]));

        spellcheck.setLanguage(LANG);
    }));

    it('can spellcheck using multiple dictionaries',
    inject(function(spellcheck, dictionaries, $q, $rootScope) {
        var p = createParagraph('test what if foo bar baz');

        spellcheck.errors(p).then(assignErrors);
        $rootScope.$digest();
        expect(errors).toContain({word: 'test', index: 0});
        expect(errors).toContain({word: 'if', index: 10});
        expect(dictionaries.getActive).toHaveBeenCalledWith(LANG);
    }));

    it('can add words to user dictionary', inject(function(spellcheck, api, $rootScope) {
        var p = createParagraph('test');

        spyOn(api, 'save');
        spellcheck.errors(p).then(assignErrors);
        $rootScope.$digest();
        expect(errors.length).toBe(1);

        spellcheck.addWordToUserDictionary('test');

        spellcheck.errors(p).then(assignErrors);
        $rootScope.$digest();

        expect(errors.length).toBe(0);
    }));

    it('can suggest', inject(function(spellcheck, api, $q) {
        spyOn(api, 'save').and.returnValue($q.when({}));
        spellcheck.suggest('test');
        expect(api.save).toHaveBeenCalledWith('spellcheck', {word: 'test', language_id: LANG});
    }));

    it('can reset dict when language is set to null', inject(function(spellcheck, $rootScope) {
        spellcheck.setLanguage(null);
        var then = jasmine.createSpy('then');
        spellcheck.errors('test').then(then);
        $rootScope.$digest();
        expect(then).not.toHaveBeenCalled();
    }));

    function assignErrors(_errors) {
        errors.splice(0, errors.length);
        errors.push.apply(errors, _errors);
    }

    function createParagraph(text) {
        var p = document.createElement('p');
        p.contentEditable = 'true';
        p.innerHTML = text;
        document.body.appendChild(p);
        return p;
    }

    describe('spellcheck menu', function() {
        it('can toggle auto spellcheck', inject(function(editor, $controller, $rootScope) {
            var ctrl = $controller('SpellcheckMenu');
            expect(ctrl.isAuto).toBe(true);

            ctrl.pushSettings();
            expect(editor.settings.spellcheck).toBe(true);

            ctrl.isAuto = false;
            ctrl.pushSettings();
            expect(editor.settings.spellcheck).toBe(false);

            spyOn(editor, 'render');
            ctrl.spellcheck();
            expect(editor.render).toHaveBeenCalled();
        }));
    });
});
