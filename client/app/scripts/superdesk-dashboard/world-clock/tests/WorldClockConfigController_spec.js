
/**
* Module with tests for the WorldClockConfigController
*
* @module WorldClockConfigController tests
*/
describe('WorldClockConfigController', function () {
    'use strict';

    var getTzdataDeferred,
        fakeTzdata,
        scope;

    beforeEach(module('superdesk.dashboard.world-clock'));

    beforeEach(inject(function ($controller, $rootScope, $q) {
        scope = $rootScope.$new();
        scope.configuration = {};

        getTzdataDeferred = $q.defer();
        fakeTzdata = {
            $promise: getTzdataDeferred.promise,
            zones: {},
            links: {}
        };

        $controller('WorldClockConfigController', {
            $scope: scope,
            tzdata: fakeTzdata
        });
    }));

    it('initializes the list of available time zone in scope', function () {
        var expectedList,
            serverTzdata;

        scope.availableZones = [];  // make sure it is initially empty

        serverTzdata = {
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
        fakeTzdata.getTzNames = function () {
            return ['Australia/Sydney', 'Europe/Rome', 'Foo/Bar'];
        };

        getTzdataDeferred.resolve(serverTzdata);
        scope.$digest();

        expectedList = ['Australia/Sydney', 'Europe/Rome', 'Foo/Bar'];
        expect(scope.availableZones).toEqual(expectedList);
    });

});
