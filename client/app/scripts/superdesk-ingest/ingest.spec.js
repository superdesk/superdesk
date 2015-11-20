
describe('ingest', function() {
    'use strict';

    describe('send service', function() {

        beforeEach(module('superdesk.ingest.send'));
        beforeEach(module('superdesk.templates-cache'));

        it('can send an item', inject(function(send, api, $q, $rootScope) {
            spyOn(api, 'save').and.returnValue($q.when({_created: 'now'}));
            var item = {_id: '1'};

            expect(send.one(item).then).toBeDefined();
            $rootScope.$digest();

            expect(api.save).toHaveBeenCalled();
            expect(item.archived).toBe('now');
        }));

        it('can send multiple items', inject(function(send, api, $q, $rootScope) {
            spyOn(api, 'save').and.returnValue($q.when({}));
            var items = [{_id: 1}, {_id: 2}];

            send.all(items);
            $rootScope.$digest();

            expect(api.save.calls.count()).toBe(2);
        }));

        it('can send an item as', inject(function(send, api, $q, $rootScope) {
            var item = {_id: 1},
                config = {
                    desk: 'desk1',
                    stage: 'stage1',
                    macro: 'macro1'
                };

            spyOn(api, 'save').and.returnValue($q.when({_created: 'now'}));

            expect(send.oneAs(item, config).then).toBeDefined();
            $rootScope.$digest();

            expect(api.save).toHaveBeenCalled();
            expect(item.archived).toBe('now');
        }));

        it('can send multiple items as', inject(function(send, api, $q, $rootScope) {
            spyOn(api, 'save').and.returnValue($q.when({_id: 'foo', _created: 'now'}));

            var items = [{_id: 1}, {_id: 2}];
            expect(send.config).toBe(null);

            var archives;
            send.allAs(items).then(function(_archives) {
                archives = _archives;
            });

            send.config.resolve({desk: 'desk1', stage: 'stage1'});
            $rootScope.$digest();

            expect(api.save.calls.count()).toBe(2);
            expect(archives.length).toBe(2);
            expect(items[0].archived).toBe('now');
        }));
    });

    describe('registering activities in superdesk.ingest module', function () {

        beforeEach(module('superdesk.ingest'));

        describe('the "archive" activity', function () {
            var activity;

            beforeEach(inject(function (superdesk) {
                activity = superdesk.activities.archive;
                if (angular.isUndefined(activity)) {
                    fail('Activity "archive" is not registered.');
                }
            }));

            it('is allowed if the current desk is not "personal"', function () {
                var extraCondition = activity.additionalCondition,
                    fakeDesks;

                // get the function that checks the additional conditions
                extraCondition = extraCondition[extraCondition.length - 1];
                fakeDesks = {
                    getCurrentDeskId: function () {
                        return '1234';
                    }
                };

                expect(extraCondition(fakeDesks)).toBe(true);
            });

            it('is not allowed if the current desk is "personal"', function () {
                var extraCondition = activity.additionalCondition,
                    fakeDesks;

                // get the function that checks the additional conditions
                extraCondition = extraCondition[extraCondition.length - 1];
                fakeDesks = {
                    getCurrentDeskId: function () {
                        return null;
                    }
                };

                expect(extraCondition(fakeDesks)).toBe(false);
            });
        });
    });

    describe('sdIngestRoutingSchedule directive', function () {
        var fakeTzData,
            getTzDataDeferred,
            isoScope;  // the directive's isolate scope

        beforeEach(module('superdesk.ingest'));
        beforeEach(module('superdesk.templates-cache'));

        beforeEach(module(function($provide) {
            var childDirectives = [
                'sdWeekdayPicker', 'sdTimepickerAlt', 'sdTypeahead'
            ];

            fakeTzData = {
                $promise: null,
                zones: {},
                links: {}
            };
            $provide.constant('tzdata', fakeTzData);

            // Mock child directives to test the directive under test in
            // isolation, avoiding the need to create more complex fixtures
            // that satisfy any special child directives' requirements.
            childDirectives.forEach(function (directiveName) {
                // Internally, Angular appends the "Directive" suffix to
                // directive name, thus we need to do the same for mocking.
                directiveName += 'Directive';
                $provide.factory(directiveName, function () {
                    return {};
                });
            });
        }));

        beforeEach(inject(function ($compile, $rootScope, $q, tzdata) {
            var element,
                html = '<div sd-ingest-routing-schedule></div>',
                scope;

            getTzDataDeferred = $q.defer();
            fakeTzData.$promise = getTzDataDeferred.promise;

            scope = $rootScope.$new();
            element = $compile(html)(scope);
            scope.$digest();

            isoScope = element.isolateScope();

            // the (mocked) routing rule being edited
            isoScope.rule = {
                schedule: {}
            };
        }));

        it('initially clears the time zone search term', function () {
            expect(isoScope.tzSearchTerm).toEqual('');
        });

        it('initializes the list of matching time zones to an empty list',
            function () {
                expect(isoScope.matchingTimeZones).toEqual([]);
            }
        );

        it('initializes the list of all available time zones', function () {
            var serverTzData = {
                zones: {
                    'Europe/Rome': ['1 - CET'],
                    'Australia/Sydney': ['10 ADN EST']
                },
                links: {
                    'Foo/Bar': []
                }
            };
            fakeTzData.zones = serverTzData.zones;
            fakeTzData.links = serverTzData.links;
            fakeTzData.getTzNames = function () {
                return ['Australia/Sydney', 'Europe/Rome', 'Foo/Bar'];
            };

            isoScope.timeZones = [];

            getTzDataDeferred.resolve(serverTzData);
            isoScope.$digest();

            expect(isoScope.timeZones).toEqual(
                ['Australia/Sydney', 'Europe/Rome', 'Foo/Bar']
            );
        });

        describe('scope\'s searchTimeZones() method', function () {
            it('sets the time zone search term to the given term ',
                function () {
                    isoScope.tzSearchTerm = 'foo';
                    isoScope.searchTimeZones('bar');
                    expect(isoScope.tzSearchTerm).toEqual('bar');
                }
            );

            it('sets the matching time zones to an empty list if given ' +
                'an empty search term',
                function () {
                    isoScope.matchingTimeZones = ['foo', 'bar'];
                    isoScope.searchTimeZones('');
                    expect(isoScope.matchingTimeZones).toEqual([]);
                }
            );

            it('sets the matching time zones to those matching the given ' +
                'search term',
                function () {
                    isoScope.timeZones = [
                        'Foo/City', 'Asia/FooBar', 'EU_f/oo', 'bar_fOo', 'xyz'
                    ];
                    isoScope.searchTimeZones('fOO');
                    expect(isoScope.matchingTimeZones).toEqual([
                        'Foo/City', 'Asia/FooBar', 'bar_fOo'
                    ]);
                }
            );
        });

        describe('scope\'s selectTimeZone() method', function () {
            it('sets the routing rule\'s time zone to the one given',
                function () {
                    isoScope.rule.schedule.time_zone = null;
                    isoScope.selectTimeZone('foo');
                    expect(isoScope.rule.schedule.time_zone).toEqual('foo');
                }
            );

            it('clears the time zone search term', function () {
                isoScope.tzSearchTerm = 'Europe';
                isoScope.selectTimeZone('foo');
                expect(isoScope.tzSearchTerm).toEqual('');
            });
        });

        describe('scope\'s clearSelectedTimeZone() method', function () {
            it('clears the routing rule\'s time zone', function () {
                isoScope.rule.schedule.time_zone = 'foo';
                isoScope.clearSelectedTimeZone();
                expect(isoScope.rule.schedule.time_zone).toBe(null);
            });
        });
    });

});
