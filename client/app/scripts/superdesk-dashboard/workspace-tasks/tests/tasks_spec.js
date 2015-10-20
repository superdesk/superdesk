
describe('tasks', function() {

    'use strict';

    beforeEach(module('superdesk.desks'));
    beforeEach(module('superdesk.filters'));
    beforeEach(module('superdesk.ui'));
    beforeEach(module('superdesk.workspace.tasks'));

    describe('task controller', function() {

        var scope;
        var desk = {incoming_stage: 'inbox'};

        beforeEach(inject(function($rootScope, $controller, $q, desks) {
            spyOn(desks, 'getCurrentDeskId').and.returnValue(1);
            spyOn(desks, 'fetchDesks').and.returnValue($q.when());
            spyOn(desks, 'fetchDeskStages').and.returnValue($q.when([]));
            spyOn(desks, 'getCurrentDesk').and.returnValue(desk);
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

        describe('kanban', function() {

            var result = {_items: []};

            beforeEach(inject(function($rootScope, $q, api) {
                spyOn(api, 'query').and.returnValue($q.when(result));
                $rootScope.$digest();
            }));

            it('can get published', inject(function(api) {
                expect(scope.published).toBe(result);
                var publishedArgs = api.query.calls.argsFor(0);
                expect(publishedArgs[0]).toBe('published');
                expect(publishedArgs[1].source.filter.bool.must.term).toEqual({'task.desk': 1});
                expect(publishedArgs[1].source.filter.bool.must_not.term).toEqual({package_type: 'takes'});
            }));

            it('can get scheduled', inject(function(api, moment) {
                expect(scope.scheduled).toBe(result);
                var scheduledArgs = api.query.calls.argsFor(1);
                expect(scheduledArgs[0]).toBe('content_templates');
                expect(scheduledArgs[1].where.template_desk).toBe(1);
                expect(moment(scheduledArgs[1].where.next_run.$gte).unix()).toBeLessThan(moment().unix());
                expect(moment(scheduledArgs[1].where.next_run.$lte).unix()).toBeGreaterThan(moment().unix());
            }));

            it('can fetch tasks', inject(function(api, $timeout) {
                $timeout.flush(500);
                var tasksArgs = api.query.calls.argsFor(2);
                expect(tasksArgs[0]).toBe('tasks');
            }));
        });
    });

    describe('pick task controller', function() {
        beforeEach(module('superdesk.workspace.tasks'));

        it('can pick task', inject(function(superdesk) {
            spyOn(superdesk, 'intent');
            var data = {item: {_id: 'foo'}};
            superdesk.start(superdesk.activity('pick.task'), {data: data});
            expect(superdesk.intent).toHaveBeenCalledWith('edit', 'item', data.item);
        }));
    });
});
