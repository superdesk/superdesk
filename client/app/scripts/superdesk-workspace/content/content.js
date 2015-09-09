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
        .directive('sdTemplateSelect', TemplateSelectDirective)
        ;

    ContentService.$inject = ['api', 'superdesk', 'templates', 'desks', 'packages', 'archiveService'];
    function ContentService(api, superdesk, templates, desks, packages, archiveService) {

        var TEXT_TYPE = 'text';

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
            var item = {type: type || TEXT_TYPE, version: 0};
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
            var data = item ? {items: [item], version: 0} : {version: 0};
            return packages.createEmptyPackage(data);
        };

        /**
         * Create new item using given template
         *
         * @param {Object} template
         * @return {Promise}
         */
        this.createItemFromTemplate = function(template) {
            var item = _.pick(template, templates.TEMPLATE_METADATA);
            return save(item).then(function(newItem) {
                templates.addRecentTemplate(desks.activeDeskId, template._id);
                return newItem;
            });
        };
    }

    ContentCreateDirective.$inject = ['api', 'desks', 'templates', 'content', 'authoringWorkspace', 'superdesk'];
    function ContentCreateDirective(api, desks, templates, content, authoringWorkspace, superdesk) {
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
            }
        };
    }

    TemplateSelectDirective.$inject = ['api', 'desks', 'templates'];
    function TemplateSelectDirective(api, desks, templates) {
        var PAGE_SIZE = 10;

        return {
            templateUrl: 'scripts/superdesk-workspace/content/views/sd-template-select.html',
            scope: {
                selectAction: '=',
                open: '='
            },
            link: function(scope) {
                scope.maxPage = 1;
                scope.options = {
                    keyword: null,
                    page: 1
                };
                scope.templates = null;

                scope.close = function() {
                    scope.open = false;
                };

                scope.select = function(template) {
                    scope.selectAction(template);
                };

                var fetchTemplates = function() {
                    templates.fetchTemplates(scope.options.page, PAGE_SIZE, 'create', desks.activeDeskId, scope.options.keyword)
                    .then(function(result) {
                        scope.maxPage = Math.ceil(result._meta.total / PAGE_SIZE);
                        scope.templates = result;
                    });
                };

                scope.$watchCollection('options', fetchTemplates);
                scope.$watch(function() {
                    return desks.activeDeskId;
                }, fetchTemplates);
            }
        };
    }
})();
