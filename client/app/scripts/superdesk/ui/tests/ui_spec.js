
'use strict';

describe('superdesk ui', function() {

    beforeEach(module('superdesk.ui'));

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
});
