'use strict';

describe('workspace', function() {

    var DESK = 1;

    beforeEach(module('templates'));
    beforeEach(module('superdesk.dashboard'));

    beforeEach(inject(function(session) {
        session.identity = {_id: 'u1'};
    }));

    beforeEach(inject(function(desks, $q) {
        spyOn(desks, 'initialize').and.returnValue($q.when());
        desks.initActive();
        desks.active.desk = DESK;
    }));

    it('can open workspace', inject(function($controller, api, desks, $q, $rootScope) {
        var workspace = {name: 'foo', widgets: [{_id: 'foo'}]};
        spyOn(api, 'query').and.returnValue($q.when({_items: [workspace]}));

        var ctrl = $controller('DashboardController', {
            widgets: [{_id: 'foo', name: 'foo'}],
            $scope: $rootScope.$new()
        });

        $rootScope.$digest();

        expect(ctrl.current.name).toBe('foo');
        expect(ctrl.widgets.length).toBe(1);
        expect(ctrl.widgets[0].name).toBe('foo');
        expect(api.query).toHaveBeenCalledWith('workspaces', {where: {desk: DESK}});
    }));

    it('can create desk workspace', inject(function($controller, api, desks, $q, $rootScope) {
        spyOn(api, 'query').and.returnValue($q.when({_items: []}));

        var ctrl = $controller('DashboardController', {
            widgets: [
                {_id: 'foo', name: 'foo'},
                {_id: 'bar', name: 'bar'},
                {_id: 'baz', name: 'baz'}
            ],
            $scope: $rootScope.$new()
        });

        $rootScope.$digest();
        expect(ctrl.availableWidgets.length).toBe(3);

        spyOn(api, 'save').and.returnValue($q.when({widgets: [{_id: 'foo'}]}));
        ctrl.selectWidget(ctrl.availableWidgets[0]);
        ctrl.addWidget(ctrl.selectedWidget);

        expect(ctrl.widgets.length).toBe(1);
        expect(ctrl.availableWidgets.length).toBe(2);
        expect(ctrl.selectedWidget).toBe(null);
        expect(api.save).toHaveBeenCalledWith('workspaces', ctrl.current, {desk: DESK, widgets: [{_id: 'foo'}]});

        $rootScope.$digest();
        expect(ctrl.widgets[0].name).toBe('foo');
    }));
});
