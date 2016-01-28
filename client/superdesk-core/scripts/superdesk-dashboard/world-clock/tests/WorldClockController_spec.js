
/**
* Module with tests for the WorldClockController
*
* @module WorldClockController tests
*/
describe('WorldClockController', function () {
    'use strict';

    var ctrl,
        getTzdataDeferred,
        fakeTzdata,
        scope;

    beforeEach(module('superdesk.dashboard.world-clock'));

    beforeEach(inject(function ($controller, $rootScope, $q) {
        scope = $rootScope.$new();

        getTzdataDeferred = $q.defer();
        fakeTzdata = {
            $promise: getTzdataDeferred.promise,
            zones: {},
            links: {}
        };

        ctrl = $controller('WorldClockController', {
            $scope: scope,
            tzdata: fakeTzdata
        });
    }));

    it('adds time zone data to Moment library on initialization', function () {
        var serverTzdata = {
            zones: {
                'Europe/Rome': ['1 - CET'],
                'Australia/Sydney': ['10 ADN EST']
            },
            links: {
                'Foo/Bar': []
            }
        };
        fakeTzdata.zones = serverTzdata.zones;
        fakeTzdata.links = serverTzdata.links;

        spyOn(ctrl._moment.tz, 'add');
        getTzdataDeferred.resolve(serverTzdata);
        scope.$digest();

        expect(ctrl._moment.tz.add).toHaveBeenCalledWith(serverTzdata);
    });

});
