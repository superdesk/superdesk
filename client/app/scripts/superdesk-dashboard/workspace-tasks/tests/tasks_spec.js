
define(['superdesk/filters'], function(filters) {
    'use strict';
    describe('tasks', function() {

        beforeEach(module('superdesk.desks'));
        beforeEach(module('superdesk.filters'));
        beforeEach(module('superdesk.ui'));
        beforeEach(module('superdesk.workspace.tasks'));

        describe('task controller', function() {

            it('can create task', inject(function($rootScope, $controller, $filter, desks) {
                spyOn(desks, 'getCurrentDeskId').and.returnValue(1);
                var scope;
                scope = $rootScope.$new();
                $controller('TasksController', {$scope: scope, $filter: $filter});
                expect(scope.newTask).toBeNull();
                scope.create();
                expect(scope.newTask.task.desk).toBe(1);
                expect(scope.newTask.task.due_date).not.toBeNull();
                expect(scope.newTask.task.due_time).not.toBeNull();
            }));
        });
    });
});
