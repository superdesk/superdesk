'use strict';

describe('content filters', function() {

    var $scope;
    beforeEach(module('superdesk.content_filters'));
    beforeEach(module('superdesk.mocks'));

    beforeEach(inject(function($rootScope, $controller, contentFilters,
        $q, api, $location, $window, notify) {
        $scope = $rootScope.$new();
        $controller('ProductionTestCtrl',
            {
                $scope: $scope,
                $location: $location,
                $window: $window,
                'notify': notify,
                'contentFilters': contentFilters
            }
        );
    }));

    it('can call production test for matching results',
    inject(function($rootScope, notify, contentFilters, $timeout, $q, api, $window) {
        var diff = {'filter_id': '559ba1c91024548825803cc4', 'return_matching': true};
        var toMatch = [{source: 'test'}];
        spyOn(api, 'save').and.returnValue($q.when({match_results: toMatch}));
        $scope.selectedfilter = '559ba1c91024548825803cc4';
        $scope.model.selectedType = 'true';
        $scope.fetchResults();

        $rootScope.$digest();
        $timeout.flush(1500);
        expect(api.save).toHaveBeenCalledWith('content_filter_tests', {}, diff);
        expect($scope.testResult).toBe(toMatch);
    }));

    it('can call production test for non-matching results',
    inject(function($rootScope, notify, contentFilters, $timeout, $q, api, $window) {
        var diff = {'filter_id': '559ba1c91024548825803cc5', 'return_matching': false};
        var toMatch = [];
        spyOn(api, 'save').and.returnValue($q.when({match_results: toMatch}));
        $scope.selectedfilter = '559ba1c91024548825803cc5';
        $scope.model.selectedType = 'false';
        $scope.fetchResults();

        $rootScope.$digest();
        $timeout.flush(1500);
        expect(api.save).toHaveBeenCalledWith('content_filter_tests', {}, diff);
        expect($scope.testResult.length).toBe(0);
    }));
});
