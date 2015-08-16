define(['superdesk/filters'], function(filters) {
    'use strict';
    describe('metadata', function() {

        beforeEach(module('superdesk.desks'));
        beforeEach(module('superdesk.ui'));
        beforeEach(module('superdesk.filters'));
        beforeEach(module('superdesk.authoring.metadata'));

        describe('metatdata controller', function() {

            it('can resolve schedule datetime', inject(function($rootScope, $controller, $filter) {
                var scope;
                scope = $rootScope.$new();
                scope.item = {publish_schedule: '2015-08-01T15:12:34+00:00'};
                $controller('MetadataWidgetCtrl', {$scope: scope, $filter: $filter});
                expect(scope.item.publish_schedule_date).toBe('08/01/2015');
                expect(scope.item.publish_schedule_time).toBe('15:12:34');
            }));
        });
    });
});
