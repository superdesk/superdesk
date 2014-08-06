define(['./module', 'angular'], function(DashboardModule, angular) {
    'use strict';

    var USER_URL = '/users/1';

    describe('dashboard', function() {

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

            $provide.provider('api', function() {
                this.api = function() {};
                this.$get = function($q) {
                    return {
                        users: {
                            widgets: {},
                            getByUrl: function(url) {
                                return $q.when(this.widgets);
                            },
                            save: function(dest, diff) {
                                return;
                            }
                        }
                    };
                };
            });
        }));

        beforeEach(module('superdesk.dashboard'));

        function getWidget() {
            var widget;
            inject(function(widgets) {
                widget = {_id: widgets[0]._id, row: 1, col: 1, sizex: 1, sizey: 1, configuration: widgets[0].configuration};
            });
            return widget;
        }

        function getScope(widgets) {
            var scope;
            inject(function(superdesk, api, $controller, $rootScope) {
                scope = $rootScope.$new(true);
                api.users.widgets = widgets ? {workspace: {widgets: widgets}} : {};
                $controller(superdesk.activity['/workspace'].controller, {$scope: scope});
                $rootScope.$apply();
            });

            return scope;
        }

        it('can render load user widgets', inject(function() {
            var scope = getScope();
            expect(scope.userWidgets.length).toBe(0);
            expect(scope.availableWidgets.length).toBe(1);
        }));

        it('can add widget to user workspace', inject(function(api, $q, $rootScope) {
            var scope = getScope();

            spyOn(api.users, 'save').andReturn($q.when());

            scope.addWidget(scope.availableWidgets[0]);
            $rootScope.$apply();

            expect(scope.userWidgets.length).toBe(1);
            expect(scope.availableWidgets.length).toBe(1);
            expect(api.users.save).toHaveBeenCalled();
        }));

        it('can load stored widgets', inject(function() {
            var scope = getScope([getWidget()]);
            expect(scope.userWidgets.length).toBe(1);
            expect(scope.userWidgets[0].label).toBe(scope.availableWidgets[0].label);
        }));
    });
});
