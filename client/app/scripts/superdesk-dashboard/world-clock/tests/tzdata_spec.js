
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

    describe('getTzNames() method', function () {
        it('returns an empty list if the data has not been fetched yet',
            function () {
                var result,
                    serverResponse;

                serverResponse = {
                    zones: {
                        'Europe/Rome': ['1 - CET'],
                        'Australia/Sydney': ['10 ADN EST'],
                        'Pacific/Auckland': ['13 NZDT']
                    },
                    links: {
                        'Foo/Bar': []
                    }
                };
                $httpBackend.whenGET(/.+/).respond(serverResponse);

                // NOTE: no .flush(), simulate no response from the server yet

                result = tzdata.getTzNames();
                expect(result).toEqual([]);
            }
        );

        it('returns a sorted list of available time zone names', function () {
            var result,
                serverResponse;

            serverResponse = {
                zones: {
                    'Europe/Rome': ['1 - CET'],
                    'Australia/Sydney': ['10 ADN EST'],
                    'Pacific/Auckland': ['13 NZDT']
                },
                links: {
                    'Foo/Bar': []
                }
            };
            $httpBackend.whenGET(/.+/).respond(serverResponse);

            $httpBackend.flush();
            $rootScope.$digest();

            result = tzdata.getTzNames();
            expect(result).toEqual([
                'Australia/Sydney', 'Europe/Rome',
                'Foo/Bar', 'Pacific/Auckland'
            ]);
        });
    });
});
