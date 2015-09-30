
'use strict';

describe('tasks', function() {

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

        it('can fetch published/scheduled', inject(function($rootScope, $q, api, moment) {
            var result = {_items: []};
            spyOn(api, 'query').and.returnValue($q.when(result));
            $rootScope.$digest();
            expect(api.query.calls.count()).toBe(2);

            expect(scope.published).toBe(result);
            var publishedArgs = api.query.calls.argsFor(0);
            expect(publishedArgs[0]).toBe('published');
            expect(publishedArgs[1].source.filter.bool.must.term).toEqual({'task.desk': 1});
            expect(publishedArgs[1].source.filter.bool.must_not.term).toEqual({package_type: 'takes'});

            expect(scope.scheduled).toBe(result);
            var scheduledArgs = api.query.calls.argsFor(1);
            expect(scheduledArgs[0]).toBe('content_templates');
            expect(scheduledArgs[1].where.template_desk).toBe(1);
            expect(moment(scheduledArgs[1].where.next_run.$gte).unix()).toBeLessThan(moment().unix());
            expect(moment(scheduledArgs[1].where.next_run.$lte).unix()).toBeGreaterThan(moment().unix());
        }));
    });
});
