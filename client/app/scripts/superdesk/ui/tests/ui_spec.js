
'use strict';

describe('superdesk ui', function() {

    beforeEach(module('superdesk.ui'));
    beforeEach(module('superdesk.templates-cache'));

    var datetimeHelper;

    describe('datetimeHelper service', function () {
        beforeEach(inject(function (_datetimeHelper_) {
            datetimeHelper = _datetimeHelper_;
        }));

        it('should be defined', function () {
            expect(datetimeHelper).toBeDefined();
        });

        it('should validate time', function() {
            expect(datetimeHelper.isValidTime('15:14:13')).toBe(true);
            expect(datetimeHelper.isValidTime('00:00:00')).toBe(true);
            expect(datetimeHelper.isValidTime('23:00:11')).toBe(true);
            expect(datetimeHelper.isValidTime('15:14:')).toBe(false);
            expect(datetimeHelper.isValidTime('15:14')).toBe(false);
            expect(datetimeHelper.isValidTime('15:14:1o')).toBe(false);
            expect(datetimeHelper.isValidTime('24:01:15')).toBe(false);
        });

        it('should validate date', function() {
            expect(datetimeHelper.isValidDate('23/09/2015')).toBe(true);
            expect(datetimeHelper.isValidDate('23/09/15')).toBe(false);
            expect(datetimeHelper.isValidDate('23/O9/2015')).toBe(false);
            expect(datetimeHelper.isValidDate('09/23/2015')).toBe(false);
            expect(datetimeHelper.isValidDate('00/09/2015')).toBe(false);
            expect(datetimeHelper.isValidDate('01/01/2015')).toBe(true);
            expect(datetimeHelper.isValidDate('1/1/15')).toBe(false);
        });
    });

    describe('sd-timepicker-alt directive', function() {
        var getTzdataDeferred,
            tzdataMock = {},  // mocked tzdata service
            $compile,
            $rootScope;

        function format(num) {
            return ('00' + num.toString(10)).slice(-2);
        }

        /**
         * Compiles the directive under test and links it with a new scope
         * containing the provided scope values.
         *
         * @function compileDirective
         * @param {Object} scopeValues - values in the current scope of the DOM
         *   element the directive will be applied to
         * @param {boolean} [noUtcConvert=false] - whether or not to compile
         *   the directive with the noUtcConvert option enabled
         * @return {Object} - the root DOM node of the compiled directive
         *   element
         */
        function compileDirective(scopeValues, noUtcConvert) {
            var html,
                scope,  // the scope of the element the directive is applied to
                $element;

            scope = $rootScope.$new();
            angular.extend(scope, scopeValues);

            html = [
                '<div sd-timepicker-alt data-model="schedule.at" ',
                    noUtcConvert ? 'no-utc-convert="true"' : '',
                '></div>'
            ].join('');

            $element = $compile(html)(scope);
            scope.$digest();

            return $element;
        }

        // mock the tzdata service that gets injected into the directive
        beforeEach(function () {
            module(function ($provide) {
                $provide.value('tzdata', tzdataMock);
            });
        });

        beforeEach(inject(function(_$compile_, _$rootScope_, $q) {
            $compile = _$compile_;
            $rootScope = _$rootScope_;

            getTzdataDeferred = $q.defer();
            tzdataMock.$promise = getTzdataDeferred.promise;
            tzdataMock.zones = {};
            tzdataMock.links = {};
        }));

        it('sets the hasValue flag if the model has a value', function () {
            var elem,
                isoScope,
                parentModel;

            parentModel = {
                schedule: {at: '0000'}
            };

            elem = compileDirective(parentModel);
            isoScope = elem.isolateScope();

            expect(isoScope.hasValue).toBe(true);
        });

        it('clears the hasValue flag if the model does not have a value',
            function () {
                var elem,
                    isoScope,
                    parentModel;

                parentModel = {
                    schedule: {at: ''}
                };

                elem = compileDirective(parentModel);
                isoScope = elem.isolateScope();

                expect(isoScope.hasValue).toBe(false);
            }
        );

        it('can render local time and set utc time', function() {
            var now = new Date();

            var scopeValues = {
                schedule: {
                    at: format(now.getUTCHours()) + format(now.getUTCMinutes())
                }
            };
            var elem = compileDirective(scopeValues);
            var iscope = elem.isolateScope();

            expect(iscope.hours).toBe(now.getHours());
            expect(iscope.minutes).toBe(now.getMinutes());

            now.setHours(now.getHours() + 1);
            iscope.setHours(now.getHours());
            expect(iscope.hours).toBe(now.getHours());
            expect(iscope.model.substr(0, 2)).toBe(format(now.getUTCHours()));

            now.setMinutes(5);
            iscope.setMinutes(now.getMinutes());
            expect(iscope.minutes).toBe(now.getMinutes());
            expect(iscope.model.substr(2, 2)).toBe(format(now.getUTCMinutes()));
        });

        describe('clearValue() scope method', function () {
            var isoScope;

            beforeEach(function () {
                var elem,
                    parentModel;

                parentModel = {
                    schedule: {at: '0000'}
                };

                elem = compileDirective(parentModel);
                isoScope = elem.isolateScope();
            });

            it('clears the hasValue flag', function () {
                isoScope.hasValue = true;
                isoScope.clearValue();
                expect(isoScope.hasValue).toBe(false);
            });

            it('resets the model value', function () {
                isoScope.hours = 10;
                isoScope.minutes = 20;
                isoScope.model = '1020';

                isoScope.clearValue();

                expect(isoScope.hours).toEqual(0);
                expect(isoScope.minutes).toEqual(0);
                expect(isoScope.model).toEqual('');
            });
        });

        describe('converting to UTC disabled', function () {
            var isoScope,
                parentModel,
                $elem;

            beforeEach(function () {
                var fakeNow = new Date('2015-09-22T15:45:07+05:30');

                fakeNow = new Date('2015-09-22T15:45:07+05:30');  // 10:15 UTC
                jasmine.clock().mockDate(fakeNow);

                parentModel = {
                    schedule: {at: '1850'}
                };
                $elem = compileDirective(parentModel, true);
                isoScope = $elem.isolateScope();
            });

            it('initializes time variables to model values', function () {
                expect(isoScope.hours).toEqual(18);
                expect(isoScope.minutes).toEqual(50);
                expect(parentModel.schedule.at).toEqual('1850');
            });

            it('initializes the list of time zone in scope', function () {
                var expectedList,
                    fetchedTzData;

                fetchedTzData = {
                    zones: {
                        'Europe/Rome': ['1 - CET'],
                        'Australia/Sydney': ['10 ADN EST']
                    },
                    links: {
                        'Foo/Bar': []
                    }
                };
                tzdataMock.zones = fetchedTzData.zones;
                tzdataMock.links = fetchedTzData.links;
                tzdataMock.getTzNames = function () {
                    return ['Australia/Sydney', 'Europe/Rome', 'Foo/Bar'];
                };

                getTzdataDeferred.resolve(fetchedTzData);
                isoScope.$digest();

                expectedList = ['Australia/Sydney', 'Europe/Rome', 'Foo/Bar'];
                expect(isoScope.timeZones).toEqual(expectedList);
            });

            describe('setHours() scope method', function () {
                it('updates hours to given value (in local TZ)', function () {
                    isoScope.hours = 10;
                    isoScope.setHours(22);
                    expect(isoScope.hours).toEqual(22);
                    expect(isoScope.model).toEqual('2250');
                });

                it('sets the hasValue flag', function () {
                    isoScope.hasValue = false;
                    isoScope.setHours(1);
                    expect(isoScope.hasValue).toBe(true);
                });
            });

            describe('setMinutes() scope method', function () {
                it('updates minutes to given value (in local TZ)', function () {
                    isoScope.minutes = 6;
                    isoScope.setMinutes(37);
                    expect(isoScope.minutes).toEqual(37);
                    expect(isoScope.model).toEqual('1837');
                });

                it('sets the hasValue flag', function () {
                    isoScope.hasValue = false;
                    isoScope.setMinutes(1);
                    expect(isoScope.hasValue).toBe(true);
                });
            });
        });
    });
});
