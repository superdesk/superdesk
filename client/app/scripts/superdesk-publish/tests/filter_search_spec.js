'use strict';

describe('Filter search directive', function() {
    var $scope;

    beforeEach(module('superdesk.publish'));
    beforeEach(module('superdesk.mocks'));

    it('can perform filter search with -in- operator',
        inject(function(filters, $rootScope, $compile, api, $q, $httpBackend, $controller, notify) {
        $scope = $rootScope.$new();
        $controller('FilterSearchController', {
            $scope: $scope,
            'filters': filters,
            'notify': notify
        });
        $scope.filterCondition = {
            field: 'urgency',
            operator: 'in',
            value: '1'
        };

        var items;
        var inputParams = {
            'field': $scope.filterCondition.field,
            'operator': $scope.filterCondition.operator,
            'value': $scope.filterCondition.value
        };

        var searchResult = [{_id: '1', name: 'guido', is_active: false,
            publish_filter: {filter_id: '1', filter_type: 'permitting'}}];

        spyOn(api, 'query').and.returnValue($q.when({_items: searchResult}));
        $compile('<div sd-filter-search data-search="search"></div>')($scope);
        $httpBackend.expectGET('scripts/superdesk-publish/filters/view/filter-search.html').
            respond(searchResult);

        $scope.search();

        filters.getFilterSearchResults(inputParams).then(function(result) {
            items = result;
            $scope.searchResult = items;
        });
        $scope.$digest();
        expect(items.length).toBe(1);
        expect(items).toBe($scope.searchResult);
        expect(api.query).toHaveBeenCalledWith('subscribers', {'filter_condition': inputParams});
    }));
    it('can perform filter search with like operator',
        inject(function(filters, $rootScope, $compile, api, $q, $httpBackend, $controller, notify) {
        $scope = $rootScope.$new();
        $controller('FilterSearchController', {
            $scope: $scope,
            'filters': filters,
            'notify': notify
        });
        $scope.filterCondition = {
            field: 'body_html',
            operator: 'like',
            value: 'lasky'
        };

        var items;
        var inputParams = {
            'field': $scope.filterCondition.field,
            'operator': $scope.filterCondition.operator,
            'value': $scope.filterCondition.value
        };

        var searchResult = [{_id: '2', name: 'Lasky', is_active: true,
            publish_filter: {filter_id: '2', filter_type: 'permitting'}}];

        spyOn(api, 'query').and.returnValue($q.when({_items: searchResult}));
        $compile('<div sd-filter-search data-search="search"></div>')($scope);
        $httpBackend.expectGET('scripts/superdesk-publish/filters/view/filter-search.html').
            respond(searchResult);

        $scope.search();

        filters.getFilterSearchResults(inputParams).then(function(result) {
            items = result;
            $scope.searchResult = items;
        });
        $scope.$digest();
        expect(items.length).toBe(1);
        expect(items).toBe($scope.searchResult);
        expect(api.query).toHaveBeenCalledWith('subscribers', {'filter_condition': inputParams});
    }));
});

