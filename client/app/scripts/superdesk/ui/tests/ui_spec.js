
'use strict';

describe('superdesk ui', function() {

    beforeEach(module('superdesk.ui'));
    beforeEach(module('templates'));

    var datetimeHelper;

    beforeEach(inject(function (_datetimeHelper_) {
        datetimeHelper = _datetimeHelper_;
    }));

    it('should have datetimeHelper service be defined', function () {
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

    describe('sd-timepicker-alt directive', function() {
        function format(num) {
            return ('00' + num.toString(10)).slice(-2);
        }

        it('can render local time and set utc time', inject(function($compile, $rootScope) {
            var now = new Date();
            var scope = $rootScope.$new();
            scope.schedule = {at: format(now.getUTCHours()) + format(now.getUTCMinutes())};
            var elem = $compile('<div sd-timepicker-alt data-model="schedule.at"></div>')(scope);
            scope.$digest();
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
        }));
    });
});
