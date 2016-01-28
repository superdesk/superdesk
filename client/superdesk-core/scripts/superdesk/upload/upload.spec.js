
'use strict';

describe('upload module', function() {

    beforeEach(module('superdesk.upload'));

    describe('file type validator directive', function() {
        it('can check', inject(function($rootScope, $compile) {
            var scope = $rootScope.$new();
            var elem = $compile('<input accept="text/*" ng-model="upload" sd-file-type-validator>')(scope);
            var ngModel = elem.controller('ngModel');
            ngModel.$setViewValue({type: 'text/plain'});
            expect(ngModel.$valid).toBe(true);
            ngModel.$setViewValue({type: 'image/jpeg'});
            expect(ngModel.$valid).toBe(false);
        }));
    });
});
