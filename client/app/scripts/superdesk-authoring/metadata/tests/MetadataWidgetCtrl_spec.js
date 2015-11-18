'use strict';

describe('MetadataWidgetCtrl controller', function () {
    var metadata,  // the metadata service
        metaInit,  //deferred initialization of the metadata service
        prefsGet,  //deferred result of the preferences service's get() method
        scope;

    beforeEach(module('superdesk.desks'));
    beforeEach(module('superdesk.ui'));
    beforeEach(module('superdesk.filters'));
    beforeEach(module('superdesk.authoring.metadata'));

    beforeEach(inject(function (
        $rootScope, $controller, $q, _metadata_, preferencesService
    ) {
        metadata = _metadata_;

        metaInit = $q.defer();
        prefsGet = $q.defer();

        spyOn(metadata, 'initialize').and.returnValue(metaInit.promise);
        spyOn(preferencesService, 'get').and.returnValue(prefsGet.promise);

        scope = $rootScope.$new();
        scope.item = {publish_schedule: '2015-08-01T15:12:34+00:00'};
        $controller('MetadataWidgetCtrl', {$scope: scope});
    }));

    it('can resolve schedule datetime', function() {
        expect(scope.item.publish_schedule_date).toBe('08/01/2015');
        expect(scope.item.publish_schedule_time).toBe('15:12:34');
    });

    it('initializes the list of categories to pick from in scope', function () {
        var userPrefs = {
            'categories:preferred': {
                selected: {'a': true, 'b': false, 'c': true, 'd': false}
            }
        };

        metadata.values = {
            categories: [
                {qcode: 'a'}, {qcode: 'b'}, {qcode: 'c'}, {qcode: 'd'}
            ]
        };

        // set the 'd' category to be already assigned to the article
        scope.item.anpa_category = [{qcode: 'd'}];

        metaInit.resolve();
        prefsGet.resolve(userPrefs);
        scope.$digest();

        expect(scope.availableCategories).toEqual(
            [{qcode: 'a'}, {qcode: 'c'}, {qcode: 'd'}]
        );
    });
});
