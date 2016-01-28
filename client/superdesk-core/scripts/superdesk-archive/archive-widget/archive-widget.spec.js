
'use strict';

describe('content widget', function() {

    beforeEach(module('superdesk.widgets.archive'));
    beforeEach(module('superdesk.authoring'));

    it('can open items', inject(function($controller, $rootScope, superdesk) {
        var scope = $rootScope.$new();
        $controller('ArchiveController', {$scope: scope});
        var item = {_id: 'foo'};
        spyOn(superdesk, 'intent');
        scope.actions.open.method(item);
        $rootScope.$digest();
        expect(superdesk.intent).toHaveBeenCalledWith('edit', 'item', item);
    }));
});
