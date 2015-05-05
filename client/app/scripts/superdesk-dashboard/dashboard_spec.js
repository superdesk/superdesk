'use strict';

describe('dashboard', function() {

    beforeEach(module('templates'));
    beforeEach(module('superdesk.dashboard'));

    beforeEach(inject(function(session) {
        session.identity = {_id: 'u1'};
    }));

    it('can open dashboard', inject(function($controller, api, $location, $q, $rootScope) {
        $location.search('desk', 1);
        var dashboard = {name: 'foo', widgets: [{_id: 'foo'}]};
        spyOn(api, 'query').and.returnValue($q.when({_items: [dashboard]}));

        var ctrl = $controller('DashboardController', {widgets: [
            {_id: 'foo', name: 'foo'}
        ]});
        $rootScope.$digest();

        expect(ctrl.current.name).toBe('foo');
        expect(ctrl.widgets.length).toBe(1);
        expect(ctrl.widgets[0].name).toBe('foo');
        expect(api.query).toHaveBeenCalledWith('dashboards', {where: {desk: 1}});
    }));

    it('can create dashboard', inject(function($controller, api, desks, $location, $q, $rootScope) {
        $location.search('desk', 1);
        spyOn(api, 'query').and.returnValue($q.when({_items: []}));

        var ctrl = $controller('DashboardController', {widgets: [
            {_id: 'foo', name: 'foo'},
            {_id: 'bar', name: 'bar'},
            {_id: 'baz', name: 'baz'}
        ]});

        $rootScope.$digest();
        expect(ctrl.availableWidgets.length).toBe(3);

        spyOn(api, 'save').and.returnValue($q.when({widgets: [{_id: 'foo'}]}));
        ctrl.selectWidget(ctrl.availableWidgets[0]);
        ctrl.addWidget(ctrl.selectedWidget);

        expect(ctrl.widgets.length).toBe(1);
        expect(ctrl.availableWidgets.length).toBe(2);
        expect(ctrl.selectedWidget).toBe(null);
        expect(api.save).toHaveBeenCalledWith('dashboards', ctrl.current, {desk: 1, widgets: [{_id: 'foo'}]});

        $rootScope.$digest();
        expect(ctrl.widgets[0].name).toBe('foo');
    }));
});
