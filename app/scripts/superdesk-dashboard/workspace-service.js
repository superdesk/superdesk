define(['lodash'], function(_) {
    'use strict';

    WorkspaceService.$inject = ['session', '$http'];
    function WorkspaceService(session, $http) {

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

            var parseWidgets = _.bind(function(response) {
                var allWidgets = _.indexBy(widgets, '_id');
                var userWidgets = (response.data.workspace || {widgets: []}).widgets;
                this.widgets = _.map(userWidgets, function(widget) {
                    return _.extend(allWidgets[widget._id] || {}, widget);
                });

                return this;
            }, this);

            return $http.get(session.identity._links.self.href).then(parseWidgets);
        };

        /**
         * Save widgets to server
         */
        this.save = function(widgets) {
            return $http({
                method: 'PATCH',
                url: session.identity._links.self.href,
                data: {workspace: {widgets: filter(widgets || this.widgets)}}
            });
        };
    }

    return WorkspaceService;
});
