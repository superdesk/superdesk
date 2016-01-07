(function() {
    'use strict';

    angular.module('superdesk.workspace.content', [
        'superdesk.api',
        'superdesk.archive',
        'superdesk.templates',
        'superdesk.packaging'
    ])
        .service('content', ContentService)
        .directive('sdContentCreate', ContentCreateDirective)
        .run(['keyboardManager', 'gettext', function(keyboardManager, gettext) {
            keyboardManager.register('General', 'ctrl + m', gettext('Creates new item'));
        }])
        ;

    ContentService.$inject = ['api', 'superdesk', 'templates', 'desks', 'packages', 'archiveService'];
    function ContentService(api, superdesk, templates, desks, packages, archiveService) {

        var TEXT_TYPE = 'text';

        var Item = function(type) {
            this.type = type || TEXT_TYPE;
            this.version = 0;
        };

        /**
         * Save data to content api
         *
         * @param {Object} data
         * @return {Promise}
         */
        function save(data) {
            return api.save('archive', data);
        }

        /**
         * Create an item of given type
         *
         * @param {string} type
         * @return {Promise}
         */
        this.createItem = function(type) {
            var item = new Item(type);
            archiveService.addTaskToArticle(item);
            return save(item);
        };

        /**
         * Create a package containing given item
         *
         * @param {Object} item
         * @return {Promise}
         */
        this.createPackageItem = function(item) {
            var data = item ? {items: [item]} : {};
            return packages.createEmptyPackage(data);
        };

        /**
         * Create a package containing given item
         *
         * @param {Object} item
         * @return {Promise}
         */
        this.createPackageFromItems = function(item) {
            return packages.createPackageFromItems([item]);
        };

        /**
         * Create new item using given template
         *
         * @param {Object} template
         * @return {Promise}
         */
        this.createItemFromTemplate = function(template) {
            var item = new Item(template.data.type || null);
            angular.extend(item, templates.pickItemData(template.data || {}), {template: template._id});
            archiveService.addTaskToArticle(item);
            return save(item).then(function(newItem) {
                templates.addRecentTemplate(desks.activeDeskId, template._id);
                return newItem;
            });
        };
    }

    ContentCreateDirective.$inject = ['api', 'desks', 'templates', 'content', 'authoringWorkspace', 'superdesk', 'keyboardManager'];
    function ContentCreateDirective(api, desks, templates, content, authoringWorkspace, superdesk, keyboardManager) {
        return {
            scope: true,
            templateUrl: 'scripts/superdesk-workspace/content/views/sd-content-create.html',
            link: function(scope) {
                var NUM_ITEMS = 5;

                /**
                 * Start editing given item in sidebar editor
                 *
                 * @param {Object} item
                 */
                function edit(item) {
                    authoringWorkspace.edit(item);
                }

                /**
                 * Create and start editing item of given type
                 *
                 * @param {string} type
                 */
                scope.create = function(type) {
                    content.createItem(type).then(edit);
                };

                /**
                 * Create and start editing a package
                 */
                scope.createPackage = function() {
                    content.createPackageItem().then(edit);
                };

                /**
                 * Create and start editing an item based on given package
                 *
                 * @param {Object} template
                 */
                scope.createFromTemplate = function(template) {
                    content.createItemFromTemplate(template).then(edit);
                };

                /**
                 * Start content upload modal
                 */
                scope.openUpload = function openUpload() {
                    superdesk.intent('upload', 'media');
                };

                scope.contentTemplates = null;

                scope.$watch(function() {
                    return desks.activeDeskId;
                }, function() {
                    templates.getRecentTemplates(desks.activeDeskId, NUM_ITEMS)
                    .then(function(result) {
                        scope.contentTemplates = result;
                    });
                });

                keyboardManager.bind('ctrl+m', function(e) {
                    if (e) {
                        e.preventDefault();
                    }
                    scope.create();
                });
            }
        };
    }
})();
