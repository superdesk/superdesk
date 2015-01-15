(function() {
'use strict';

ContentCtrlFactory.$inject = ['api', 'superdesk', 'workqueue'];
function ContentCtrlFactory(api, superdesk, workqueue) {
    return function ContentCtrl($scope) {
        /**
         * Create an item and start editing it
         */
        this.create = function(type) {
            var item = {type: type || 'text'};
            api('archive')
                .save(item)
                .then(function() {
                    workqueue.add(item);
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
    };
}

angular.module('superdesk.workspace.content', [])
    .factory('ContentCtrl', ContentCtrlFactory);
})();
