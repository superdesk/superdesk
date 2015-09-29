
'use strict';

define(['superdesk/filters'], function(filters) {
    describe('tasks', function() {

        beforeEach(module('superdesk.desks'));
        beforeEach(module('superdesk.filters'));
        beforeEach(module('superdesk.ui'));
        beforeEach(module('superdesk.workspace.tasks'));

        describe('task controller', function() {

            var scope;

            beforeEach(inject(function($rootScope, $controller, $q, desks) {
                spyOn(desks, 'getCurrentDeskId').and.returnValue(1);
                spyOn(desks, 'fetchDeskStages').and.returnValue($q.when([]));
                scope = $rootScope.$new();
                $controller('TasksController', {$scope: scope});
            }));

            it('can create task', inject(function($rootScope, $controller, desks) {
                expect(scope.newTask).toBeNull();
                scope.create();
                expect(scope.newTask.task.desk).toBe(1);
                expect(scope.newTask.task.due_date).not.toBeNull();
                expect(scope.newTask.task.due_time).not.toBeNull();
            }));

            it('can fetch published', inject(function($rootScope, $q, api) {
                var result = {_items: []};
                spyOn(api, 'query').and.returnValue($q.when(result));
                $rootScope.$digest();
                expect(scope.published).toBe(result);
            }));
        });
    });
});
