
'use strict';

describe('related item widget', function() {
    beforeEach(module('superdesk.widgets.relatedItem'));

    it('can open item', inject(function($rootScope, $controller, superdesk) {
        var scope = $rootScope.$new();
        $controller('relatedItemController', {$scope: scope});
        scope.$digest();

        var item = {};
        spyOn(superdesk, 'intent');
        scope.actions.open.method(item);
        expect(superdesk.intent).toHaveBeenCalledWith('edit', 'item', item);
    }));

    it('can associate item', inject(function($rootScope, api, $q, $controller, superdesk) {
        var scope = $rootScope.$new();
        scope.options = {};
        $controller('relatedItemController', {$scope: scope});
        scope.$digest();

        var item = {'priority': 1};
        spyOn(superdesk, 'intent');
        spyOn(api, 'save').and.returnValue($q.when({_items: [item]}));
        scope.options.item = {};
        scope.actions.apply.method(item);

        $rootScope.$apply();
        expect(scope.options.item.priority).toBe(1);
    }));
});
