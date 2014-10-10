define([
    'angular',
    'require',
    './workspace-controller',
    './tasks-controller',
    './workspace-service',
    './sd-widget-directive',
    './widgets-provider',
    './grid/grid',
    './world-clock/world-clock'
], function(angular, require) {
    'use strict';

    function TaskPreviewDirective() {
        return {
            templateUrl: 'scripts/superdesk-dashboard/views/task-preview.html',
            scope: {item: '='},
            link: function(scope, element, attrs) {}
        };
    }

    AssigneeViewDirective.$inject = ['desks'];
    function AssigneeViewDirective(desks) {
        desks.initialize();
        return {
            templateUrl: 'scripts/superdesk-dashboard/views/assignee-view.html',
            scope: {item: '='},
            link: function(scope) {
                scope.deskLookup = desks.deskLookup;
                scope.userLookup = desks.userLookup;
            }
        };
    }

    // to avoid circular dependency
    angular.module('superdesk.dashboard.widgets', []).
        provider('widgets', require('./widgets-provider'));

    return angular.module('superdesk.dashboard', [
        'superdesk.dashboard.widgets',
        'superdesk.dashboard.grid',
        'superdesk.dashboard.world-clock',
        'superdesk.workspace.content'
    ])

    .service('workspace', require('./workspace-service'))
    .directive('sdWidget', require('./sd-widget-directive'))
    .directive('sdTaskPreview', TaskPreviewDirective)
    .directive('sdAssigneeView', AssigneeViewDirective)

    .filter('wcodeFilter', function() {
        return function(input, values) {
            return _.pick(input, _.difference(_.keys(input), _.keys(values)));
        };
    })

    .config(['superdeskProvider', function(superdesk) {
        superdesk.activity('/workspace', {
            label: gettext('Workspace'),
            controller: require('./workspace-controller'),
            templateUrl: require.toUrl('./views/workspace.html'),
            topTemplateUrl: require.toUrl('./views/workspace-topnav.html'),
            priority: -1000,
            category: superdesk.MENU_MAIN
        });
        superdesk.activity('/workspace/tasks', {
            label: gettext('Workspace'),
            controller: require('./tasks-controller'),
            templateUrl: require.toUrl('./views/workspace-tasks.html'),
            topTemplateUrl: require.toUrl('./views/workspace-topnav.html'),
            beta: true
        });
        superdesk.activity('/workspace/stream', {
            label: gettext('Workspace'),
            templateUrl: require.toUrl('./views/workspace-stream.html'),
            topTemplateUrl: require.toUrl('./views/workspace-topnav.html'),
            beta: true
        });
        superdesk.activity('pick.task', {
            label: gettext('Pick task'),
            icon: 'pencil',
            controller: ['api', 'data', 'session', 'superdesk', 'workqueue',
                function(api, data, session, superdesk, workqueue) {
                    api('tasks').save(
                        _.clone(data.item),
                        {task: _.extend({user: session.identity._id}, data.item.task)})
                    .then(function(result) {
                        workqueue.add(result);
                        superdesk.intent('author', 'article', result);
                    });
                }
            ],
            filters: [{action: superdesk.ACTION_EDIT, type: 'task'}]
        });
    }]);
});
