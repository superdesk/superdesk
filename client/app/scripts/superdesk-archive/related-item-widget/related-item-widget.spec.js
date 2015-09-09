
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
});
