(function() {
    'use strict';

    ContentCtrlFactory.$inject = ['api', 'superdesk', 'templates', 'desks', 'archiveService'];
    function ContentCtrlFactory(api, superdesk, templates, desks, archiveService) {
        return function ContentCtrl($scope) {
            var scope = $scope;
            var self = this;

            /**
             * Create an item and start editing it
             */
            this.create = function(type) {
                if (scope && scope.dirty){
                    scope.closeOpenNew(self.createItem, type);
                } else {
                    self.createItem(type);
                }
            };

            this.createItem = function (type) {
                var item = {type: type || 'text', version: 0};
                archiveService.addTaskToArticle(item);
                api('archive').save(item).then(function() {
                    superdesk.intent('author', 'article', item);
                });
            };

            this.createPackage = function (current_item) {
                if (scope && scope.dirty){
                    scope.closeOpenNew(self.createPackageItem, current_item);
                } else {
                    self.createItem(current_item);
                }
            };

            this.createPackageItem = function (current_item) {
                if (current_item) {
                    superdesk.intent('create', 'package', {items: [current_item]});
                } else {
                    superdesk.intent('create', 'package');
                }
            };

            this.createFromTemplate = function(template) {
                if (scope && scope.dirty){
                    scope.closeOpenNew(self.createFromTemplateItem, template);
                } else {
                    self.createFromTemplateItem(template);
                }
            };

            this.createFromTemplateItem = function (template) {
                var item = _.pick(template, templates.TEMPLATE_METADATA);
                api('archive').save(item).then(function() {
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
