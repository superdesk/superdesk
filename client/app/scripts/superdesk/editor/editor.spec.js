'use strict';

describe('text editor', function() {

    beforeEach(module('superdesk.editor'));
    beforeEach(module('superdesk.editor.spellcheck'));

    beforeEach(function() {
        // remove all elements from body
        document.body = document.createElement('body');
    });

    function createScope(text, $rootScope) {
        var scope = $rootScope.$new();
        scope.node = document.createElement('p');
        scope.node.innerHTML = text;
        scope.model = {
            $viewValue: text,
            $setViewValue: function(value) {
                this.$viewValue = value;
            }
        };
        document.body.appendChild(scope.node);
        spyOn(scope.model, '$setViewValue').and.callThrough();
        return scope;
    }

    it('can spellcheck', inject(function(editor, spellcheck, $q, $rootScope) {
        spyOn(spellcheck, 'errors').and.returnValue($q.when([{word: 'test', index: 0}]));
        var scope = createScope('test', $rootScope);
        editor.registerScope(scope);
        editor.renderScope(scope);
        $rootScope.$digest();

        expect(scope.node.innerHTML).toBe('<span class="sderror sdhilite">test</span>');
    }));

    it('can remove highlights but keep marker', inject(function(editor, $q, $rootScope) {
        var content = 'test <b>foo</b> <span class="sderror sdhilite">error</span> it';
        var scope = createScope(content, $rootScope);
        var html = editor.cleanScope(scope);
        expect(html).toBe('test <b>foo</b> error it');
    }));

    it('can findreplace', inject(function(editor, spellcheck, $q, $rootScope, $timeout) {
        spyOn(spellcheck, 'errors').and.returnValue($q.when([{word: 'test', index: 0}]));
        var scope = createScope('test foo and foo', $rootScope);
        editor.registerScope(scope);

        editor.setSettings({findreplace: {needle: 'foo'}});
        editor.render();
        $timeout.flush();

        $rootScope.$digest();
        var foo = '<span class="sdfindreplace sdhilite">foo</span>';
        var fooActive = '<span class="sdfindreplace sdhilite sdactive">foo</span>';
        expect(scope.node.innerHTML).toBe('test ' + foo + ' and ' + foo);

        editor.selectNext();
        expect(scope.node.innerHTML).toBe('test ' + fooActive + ' and ' + foo);

        editor.selectNext();
        expect(scope.node.innerHTML).toBe('test ' + foo + ' and ' + fooActive);

        editor.selectPrev();
        expect(scope.node.innerHTML).toBe('test ' + fooActive + ' and ' + foo);

        editor.replace('test');
        expect(scope.node.innerHTML).toBe('test test and ' + foo);

        editor.setSettings({findreplace: {needle: 'test'}});
        editor.render();
        $timeout.flush();
        editor.replaceAll('bar');
        expect(scope.node.innerHTML).toBe('bar bar and foo');

        editor.setSettings({findreplace: null});
        editor.render();
        $rootScope.$digest();
        expect(scope.node.innerHTML).toContain('sderror');
        expect(scope.node.innerHTML).not.toContain('active');
    }));

    it('can save model value', inject(function(editor, $rootScope) {
        var scope = createScope('foo', $rootScope);
        editor.registerScope(scope);

        scope.node.innerHTML = 'foo';
        editor.commit();
        expect(scope.model.$setViewValue).not.toHaveBeenCalled();

        scope.node.innerHTML = 'bar';
        editor.commit();
        expect(scope.model.$setViewValue).toHaveBeenCalledWith('bar');

        scope.node.innerHTML = 'baz';
        editor.commit();

        editor.undo(scope);
        editor.undo(scope);
        expect(scope.node.innerHTML).toBe('foo');

        editor.redo(scope);
        expect(scope.node.innerHTML).toBe('bar');

        editor.redo(scope);
        expect(scope.node.innerHTML).toBe('baz');

        editor.undo(scope);
        editor.undo(scope);

        scope.node.innerHTML = 'test';
        editor.commit();

        editor.redo(scope);
        expect(scope.node.innerHTML).toBe('test');
    }));

    it('can check if keyboard event is important or not', inject(function(editor) {
        expect(editor.shouldIgnore({keyCode: 16})).toBe(true);
        expect(editor.shouldIgnore({keyCode: 39})).toBe(true);
        expect(editor.shouldIgnore({shiftKey: true, ctrlKey: true, keyCode: 65})).toBe(true);
        expect(editor.shouldIgnore({keyCode: 65})).toBe(false);
    }));
});
