(function() {
'use strict';

ContentCtrlFactory.$inject = ['api', 'superdesk', 'templates', 'desks', 'archiveService'];
function ContentCtrlFactory(api, superdesk, templates, desks, archiveService) {
    return function ContentCtrl($scope) {
        var templateFields = [
            'abstract',
            'anpa_take_key',
            'body_html',
            'byline',
            'dateline',
            'headline',
            'language',
            'more_coming',
            'pubstatus',
            'slugline',
            'type'
        ];

        /**
         * Create an item and start editing it
         */
        this.create = function(type) {
            var item = {type: type || 'text', version: 0};
            archiveService.addTaskToArticle(item);

            api('archive').save(item).then(
                function() {
                    superdesk.intent('author', 'article', item);
                });
        };

        this.createPackage = function createPackage(current_item) {
            if (current_item) {
                superdesk.intent('create', 'package', {items: [current_item]});
            } else {
                superdesk.intent('create', 'package');
            }
        };

        this.createFromTemplate = function(template) {
            var item = _.pick(template, templateFields);
            api('archive')
            .save(item)
            .then(function() {
                return templates.addRecentTemplate(desks.activeDeskId, template._id);
            })
            .then(function() {
                superdesk.intent('author', 'article', item);
            });
        };
    };
}

angular.module('superdesk.workspace.content', ['superdesk.templates'])
    .factory('ContentCtrl', ContentCtrlFactory);
})();
