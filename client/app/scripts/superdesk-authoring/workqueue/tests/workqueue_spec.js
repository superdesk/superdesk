
'use strict';

describe('workqueue', function() {
    var USER_ID = 'u1';

    angular.module('mock.route', ['ngRoute'])
        .config(function($routeProvider) {
            $routeProvider.when('/mock/:_id', {
                template: ''
            });
        });

    beforeEach(module('mock.route'));
    beforeEach(module('superdesk.authoring.workqueue'));

    beforeEach(inject(function(session, $q) {
        spyOn(session, 'getIdentity').and.returnValue($q.when({_id: USER_ID}));
    }));

    it('loads locked items of current user', inject(function(workqueue, api, session, $q, $rootScope) {
        var items;

        spyOn(api, 'query').and.returnValue($q.when({_items: [{}]}));

        workqueue.fetch().then(function() {
            items = workqueue.items;
        });

        $rootScope.$apply();

        expect(items.length).toBe(1);
        expect(items).toBe(workqueue.items);
        expect(api.query).toHaveBeenCalledWith('archive', {source: {filter: {term: {lock_user: USER_ID}}}});
        expect(session.getIdentity).toHaveBeenCalled();
    }));

    it('can update single item', inject(function(workqueue, api, $q, $rootScope) {
        spyOn(api, 'find').and.returnValue($q.when({_etag: 'xy'}));

        workqueue.items = [{_id: '1'}];
        workqueue.updateItem('1');

        $rootScope.$digest();

        expect(api.find).toHaveBeenCalledWith('archive', '1');
        expect(workqueue.items[0]._etag).toBe('xy');
    }));

    it('can watch route change and update active', inject(
    function(api, $location, $controller, $q, $rootScope) {
        spyOn(api, 'query').and.returnValue($q.when({_items: [{_id: 'foo'}]}));
        var scope = $rootScope.$new();
        $controller('Workqueue', {$scope: scope});
        $rootScope.$digest();
        expect(scope.active).toBe(null);

        $location.path('/mock/foo');
        $rootScope.$digest();
        expect(scope.active._id).toBe('foo');
    }));
});
