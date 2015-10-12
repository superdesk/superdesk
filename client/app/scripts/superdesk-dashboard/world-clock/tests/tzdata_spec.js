
/**
* Module with tests for the tzdata factory
*
* @module tzdata factory tests
*/
describe('tzdata factory', function () {
    'use strict';

    var tzdata,
        $httpBackend,
        $rootScope;

    beforeEach(module('superdesk.dashboard.world-clock'));

    beforeEach(inject(function (_$httpBackend_, _$rootScope_, _tzdata_) {
        tzdata = _tzdata_;
        $httpBackend = _$httpBackend_;
        $rootScope = _$rootScope_;
    }));

    it('requests correct time zone data from the server', function () {
        var expectedUrl = new RegExp(
            'superdesk-dashboard/world-clock/timezones-all.json$');

        $httpBackend.expectGET(expectedUrl).respond({zones: {}, rules: {}});
        $rootScope.$digest();

        $httpBackend.verifyNoOutstandingExpectation();
    });

    it('stores fetched timezone data on sucess response', function () {
        var response = {
            zones: {
                'Europe/Rome': ['1 - CET'],
                'Australia/Sydney': ['10 ADN EST']
            },
            links: {
                'Foo/Bar': []
            }
        };

        tzdata.zones = null;
        tzdata.links = null;
        $httpBackend.whenGET(/.+/).respond(response);

        $httpBackend.flush();
        $rootScope.$digest();

        expect(tzdata.zones).toEqual(response.zones);
        expect(tzdata.links).toEqual(response.links);
    });
});
