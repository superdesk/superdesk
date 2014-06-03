define(['./module', 'angular'], function(DashboardModule, angular) {
    'use strict';

    describe('dashboard', function() {

        var USER_URL = 'user_url/1';

        beforeEach(module(function($provide) {

            $provide.service('session', function() {
                this.identity = {
                    _links: {self: {href: USER_URL}}
                };
            });

            $provide.provider('superdesk', function() {
                var _activity = {};
                this.activity = function(id, activity) {
                    _activity[id] = activity;
                };

                this.$get = function() {
                    return {activity: _activity};
                };
            });

        }));

        beforeEach(module('superdesk.dashboard'));

        var widget;
        beforeEach(inject(function(widgets) {
            widget = {_id: widgets[0]._id, row: 1, col: 1, sizex: 1, sizey: 1, configuration: widgets[0].configuration};
        }));

        function getScope(widgets) {
            var scope;
            inject(function(superdesk, $controller, $rootScope, $httpBackend) {
                scope = $rootScope.$new(true);
                $httpBackend.expectGET(USER_URL).respond(widgets ? {workspace: {widgets: widgets}} : {});
                $controller(superdesk.activity['/dashboard'].controller, {$scope: scope});
                $httpBackend.flush();
            });

            return scope;
        }

        it('can render load user widgets', inject(function() {
            var scope = getScope();
            expect(scope.userWidgets.length).toBe(0);
            expect(scope.availableWidgets.length).toBe(1);
        }));

        it('can add widget to user workspace', inject(function($httpBackend) {
            var scope = getScope();

            $httpBackend.expectPATCH(USER_URL, {workspace: {widgets: [widget]}}).respond({});

            scope.addWidget(scope.availableWidgets[0]);

            $httpBackend.flush();

            expect(scope.userWidgets.length).toBe(1);
            expect(scope.availableWidgets.length).toBe(1);
        }));

        it('can load stored widgets', inject(function() {
            var scope = getScope([widget]);
            expect(scope.userWidgets.length).toBe(1);
            expect(scope.userWidgets[0].label).toBe(scope.availableWidgets[0].label);
        }));
    });
});
