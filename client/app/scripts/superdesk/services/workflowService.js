define([
    'lodash',
    'angular',
    './preferencesService'
], function(_, angular) {
    'use strict';

    WorkflowService.$inject = ['preferencesService'];
    function WorkflowService(preferencesService) {
        var _actions = [];

        this.isActionAllowed = function isActionAllowed(item, actionName) {

            if (_.isUndefined(actionName) || _.isUndefined(item.state)) { return true; }

            var action = _.find(_actions, function(actionItem) {
                return actionItem.name === actionName;
            });

            if (action) {
                if (!_.isEmpty(action.include_states)) {
                    return _.includes(action.include_states, item.state);
                } else if (!_.isEmpty(action.exclude_states)) {
                    return !_.includes(action.exclude_states, item.state);
                }
            }

            return false;
        };

        this.setActions = function (actions) {
            _actions = actions;
        };

        preferencesService.getActions().then(this.setActions);
    }

    WorkflowController.$inject = ['workflow'];
    function WorkflowController(workflow) {
        this.isActionAllowed = angular.bind(workflow, workflow.isActionAllowed);
    }

    return angular.module('superdesk.workflow', [])
        .service('workflow',  WorkflowService)
        .controller('Workflow', WorkflowController)
        .run(['workflow', angular.noop]) // make sure it's loaded
        ;
});
