'use strict';

describe('keyword vocabularies', function() {

    beforeEach(module('superdesk.vocabularies'));
    beforeEach(module('superdesk.authoring'));
    beforeEach(module('superdesk.authoring.metadata'));
    beforeEach(module('templates'));

    var keywords = {'_items': [
        {'_id': 'Science and Technology', 'name': 'Science and Technology', 'value': 'SciTech'},
        {'_id': 'International Health Stories', 'name': 'International Health Stories', 'value': 'Medicine'},
        {'_id': 'Health', 'name': 'Health', 'value': 'Health'}
    ]};

    var scope, modal, modalConfirm;

    beforeEach(inject(function($rootScope, $compile, api, $q, _modal_) {
        spyOn(api.vocabulary_keywords, 'query').and.returnValue($q.when(keywords));

        var elem = $compile('<div sd-admin-voc-keywords></div>')($rootScope.$new());
        scope = elem.scope();
        scope.$digest();

        modal = _modal_;
        modalConfirm = $q.defer();
        spyOn(modal, 'confirm').and.returnValue(modalConfirm.promise);
    }));

    it('can fetch active keywords and updates the metadata.values', inject(function(metadata) {
        expect(scope.keywords.length).toBe(3);
        expect(metadata.values.keywords.length).toBe(3);
    }));

    it('can save keyword', inject(function(api, $q, $rootScope) {
        scope.edit({});
        scope.editKeyword.name = 'Property';
        scope.editKeyword.value = 'Property';

        spyOn(api.vocabulary_keywords, 'save').and.returnValue($q.when());
        scope.save();

        $rootScope.$digest();
        expect(api.vocabulary_keywords.save).toHaveBeenCalledWith({}, {name: 'Property', value: 'Property'});
    }));

    it('can remove keyword', inject(function(api, $q, metadata) {
        var keywordToRemove = keywords._items.pop();
        spyOn(api.vocabulary_keywords, 'remove').and.returnValue($q.when());

        scope.remove(keywordToRemove);
        modalConfirm.resolve();
        scope.$digest();

        expect(modal.confirm).toHaveBeenCalled();
        expect(api.vocabulary_keywords.remove).toHaveBeenCalledWith(
            {_id: 'Health', name: 'Health', value: 'Health'});
        expect(metadata.values.keywords.length).toBe(2);
    }));

});
