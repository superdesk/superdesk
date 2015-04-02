'use strict';

describe('content', function() {
    var item = {_id: 1};

    beforeEach(module('templates'));
    beforeEach(module('superdesk.mocks'));
    beforeEach(module('superdesk.archive'));

    it('can spike items', inject(function(spike, api, $q) {
        spyOn(api, 'update').and.returnValue($q.when());
        spike.spike(item);
        expect(api.update).toHaveBeenCalledWith('archive_spike', item, {state: 'spiked'});
    }));

    it('can unspike items', inject(function(spike, api, $q) {
        spyOn(api, 'update').and.returnValue($q.when());
        spike.unspike(item);
        expect(api.update).toHaveBeenCalledWith('archive_unspike', item, {});
    }));

    describe('multi module', function() {
        it('can reset on route change', inject(function(multi, $rootScope) {
            multi.toggle({_id: 1});
            expect(multi.count).toBe(1);

            $rootScope.$broadcast('$routeChangeStart');
            $rootScope.$digest();

            expect(multi.count).toBe(0);
        }));
    });

    describe('media box directive', function() {
        it('can select item for multi editing', inject(function(multi, $rootScope, $compile) {
            var scope = $rootScope.$new();
            scope.item = item;

            $compile('<div sd-media-box></div>')(scope);
            scope.$digest();

            expect(scope.multi.selected).toBe(false);
            scope.toggleSelected();
            expect(scope.multi.selected).toBe(true);

            multi.reset();
            $rootScope.$digest();
            expect(scope.multi.selected).toBe(false);
        }));
    });
});
