'use strict';

describe('workspace', function() {

    var DESK = 1;

    beforeEach(module('superdesk.templates-cache'));
    beforeEach(module('superdesk.dashboard'));

    beforeEach(inject(function(session) {
        session.identity = {_id: 'u1'};
    }));

    beforeEach(inject(function(desks, $q) {
        spyOn(desks, 'initialize').and.returnValue($q.when());
        desks.initActive();
        desks.activeDesk = {_id: DESK, name: 'Desk'};
        desks.activeDeskId = DESK;
    }));

    it('can open active workspace', inject(function($controller, workspaces, $q, $rootScope) {
        var workspace = {name: 'foo', widgets: [{_id: 'foo'}]};
        workspaces.active = workspace;
        spyOn(workspaces, 'getActive');

        var ctrl = $controller('DashboardController', {
            widgets: [{_id: 'foo', name: 'foo'}],
            $scope: $rootScope.$new()
        });

        $rootScope.$digest();
        expect(ctrl.current).toBe(null);

        $rootScope.$digest();
        expect(ctrl.current.name).toBe('foo');
        expect(ctrl.widgets.length).toBe(1);
        expect(ctrl.widgets[0].name).toBe('foo');
    }));

    it('can fetch workspaces for current user', inject(function(workspaces, api, session, $q, $rootScope) {
        spyOn(api, 'query').and.returnValue({_items: []});
        session.testUser('foo');

        var items;
        workspaces.queryUserWorkspaces().then(function(_items) {
            items = _items;
        });

        $rootScope.$digest();

        expect(items).toEqual([]);
        expect(api.query).toHaveBeenCalledWith('workspaces', {where: {user: 'foo'}});
    }));

    describe('active workspace', function() {
        it('can set active workspace', inject(function(workspaces, preferencesService) {
            var active = {_id: 'test'};
            spyOn(preferencesService, 'update');
            workspaces.setActive(active);
            expect(workspaces.active).toBe(active);
            expect(preferencesService.update).toHaveBeenCalled();
        }));

        it('can set active desk',
        inject(function(workspaces, desks, api, preferencesService, $q, $rootScope) {
            spyOn(preferencesService, 'update');

            var desk = {_id: 'foo'};
            desks.deskLookup = [];
            desks.deskLookup.foo = desk;
            workspaces.setActiveDesk(desk);
            $rootScope.$digest();

            expect(preferencesService.update).toHaveBeenCalledWith(
                {'workspace:active': {workspace: 'foo'}},
                'workspace:active'
            );
        }));

        it('can create workspace', inject(function(workspaces, session, api, $q, $rootScope) {
            spyOn(api, 'save').and.returnValue($q.when({_id: 'w1'}));
            session.testUser('foo');
            var workspace = {name: 'test'};
            workspaces.save(workspace);
            $rootScope.$digest();
            expect(workspaces.active._id).toBe('w1');
            expect(api.save).toHaveBeenCalledWith('workspaces', {user: 'foo', name: 'test'});
        }));

        it('can use last active workspace',
        inject(function(workspaces, api, preferencesService, $q, $rootScope) {
            var active = {};
            spyOn(preferencesService, 'get').and.returnValue($q.when({workspace: 'w'}));
            spyOn(api, 'find').and.returnValue($q.when(active));
            workspaces.getActive();
            $rootScope.$digest();
            expect(workspaces.active).toBe(active);
            expect(api.find).toHaveBeenCalledWith('workspaces', 'w');
        }));

        it('can create desk workspace if desk is selected but no workspace',
        inject(function(workspaces, desks, api, preferencesService, $q, $rootScope) {
            spyOn(preferencesService, 'get').and.returnValue($q.when({workspace: DESK}));
            spyOn(api, 'query').and.returnValue($q.when({_items: []}));
            desks.deskLookup = [];
            desks.deskLookup[DESK] = {_id: DESK};
            workspaces.getActive();
            $rootScope.$digest();
            expect(workspaces.active.desk).toBe(DESK);
            expect(workspaces.active.widgets).toEqual([]);
            expect(api.query).toHaveBeenCalledWith('workspaces', {where: {desk: DESK}});
        }));

        it('can create user workspaces if there is no desk and no workspace',
        inject(function(workspaces, desks, session, preferencesService, $q, $rootScope) {
            spyOn(preferencesService, 'get').and.returnValue($q.when(null));
            desks.activeDeskId = null;
            session.testUser('foo');

            workspaces.getActive();
            $rootScope.$digest();

            expect(workspaces.active.desk).toBe(undefined);
            expect(workspaces.active.user).toBe('foo');
        }));
    });
    describe('sdDeskDropdown directive', function() {
        var scope, workspaces;

        beforeEach(inject(function (desks, _workspaces_, api, preferencesService, $q, $rootScope, $compile) {
            workspaces = _workspaces_;
            spyOn(desks, 'setCurrentDeskId');
            spyOn(workspaces, 'setActive');
            spyOn(preferencesService, 'update');
            desks.deskLookup = [];
            desks.deskLookup.foo = {_id: 'foo'};
            spyOn(preferencesService, 'get').and.returnValue($q.when({workspace: 'foo'}));
            spyOn(api, 'query').and.returnValue($q.when({_items: []}));

            scope = $rootScope.$new();
            $compile('<div sd-desk-dropdown></div>')(scope);
            scope.$digest();
        }));

        describe('selectDesk() scope method', function() {
            it('can set workspace type', inject(function () {
                var desk = {_id: 'foo'};
                scope.workspaceType = null;
                scope.selectDesk(desk);

                expect(scope.workspaceType).toEqual('desk');
            }));
        });

        describe('selectWorkspace() scope method', function() {
            it('can set workspace type', inject(function () {
                var workspace = {name: 'foo', widgets: [{_id: 'foo'}]};

                scope.workspaceType = null;
                scope.selectWorkspace(workspace);

                expect(scope.workspaceType).toEqual('workspace');
            }));
        });
    });
});
