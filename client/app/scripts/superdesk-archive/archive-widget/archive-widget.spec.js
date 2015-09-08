
'use strict';

describe('content widget', function() {

    beforeEach(module('superdesk.widgets.archive'));
    beforeEach(module('superdesk.authoring'));

    it('can open items', inject(function($controller, $rootScope, authoringWorkspace) {
        var scope = $rootScope.$new();
        $controller('ArchiveController', {$scope: scope});
        var item = {_id: 'foo'};
        spyOn(authoringWorkspace, 'edit');
        scope.actions.open.method(item);
        $rootScope.$digest();
        expect(authoringWorkspace.edit).toHaveBeenCalledWith(item);
    }));
});
