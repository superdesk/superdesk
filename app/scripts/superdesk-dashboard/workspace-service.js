define(['lodash'], function(_) {
    'use strict';

    WorkspaceService.$inject = ['session', 'api'];
    function WorkspaceService(session, api) {

        function filter(widgets) {
            return _.map(widgets, function(widget) {
                return _.pick(widget, ['_id', 'sizex', 'sizey', 'col', 'row', 'configuration']);
            });
        }

        /**
         * Get workspace for current user
         *
         * @param {Array} widgets
         * @return {Object} workspace
         */
        this.load = function(widgets) {

            var parseWidgets = _.bind(function(user) {
                var allWidgets = _.indexBy(widgets, '_id');
                var userWidgets = (user.workspace || {widgets: []}).widgets;
                this.widgets = _.map(userWidgets, function(widget) {
                    return _.defaults(widget, allWidgets[widget._id]);
                });

                return this;
            }, this);

            return api.users.getByUrl(session.identity._links.self.href).then(parseWidgets);
        };

        /**
         * Save widgets to server
         */
        this.save = function(widgets) {
            return api.users.save(session.identity, {workspace: {widgets: filter(widgets || this.widgets)}});
        };
    }

    return WorkspaceService;
});
