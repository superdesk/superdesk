
'use strict';

describe('packaging', function() {

    beforeEach(module('superdesk.packaging'));

    describe('package-items-edit directive', function() {

        // ignore template
        beforeEach(inject(function($templateCache) {
            $templateCache.put('scripts/superdesk-packaging/views/sd-package-items-edit.html', '');
        }));

        it('listens to package:addItems event', inject(function($compile, $rootScope) {
            var scope = $rootScope.$new();
            scope.autosave = jasmine.createSpy('autosave');
            scope.groups = [{id: 'root', 'refs': [{idRef: 'main'}]}, {id: 'main', refs: [], items: []}];
            $compile('<div sd-package-items-edit ng-model="groups"></div>')(scope);
            scope.$digest();

            expect(scope.groups[1].refs.length).toBe(0);

            var item = {_id: 'foo'};
            addItem(item);

            expect(scope.groups[1].refs.length).toBe(1);
            expect(scope.groups[1].refs[0].residRef).toBe(item._id);
            expect(scope.autosave).toHaveBeenCalled();

            addItem(item);
            expect(scope.groups[1].refs.length).toBe(1);

            function addItem(i) {
                scope.$broadcast('package:addItems', {
                    group: 'main',
                    items: [i]
                });
            }
        }));
    });
});
