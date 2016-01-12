(function() {
    'use strict';

    angular.module('superdesk.spinner', [])
        .service('spinner', function() {
            this.processCount = 0;
            this.start = function() {
                this.processCount++;
            };
            this.stop = function() {
                this.processCount = (this.processCount - 1) || 0;
            };
            this.get = function() {
                return this.processCount > 0;
            };
        })
        .directive('sdSpinner', ['spinner', function(spinner) {
            return {
                template: '<div class="item-globalsearch"><div ng-if="status" class="popup">Loading...</div></div>',
                link: function(scope, element, attrs) {
                    scope.status = false;
                    scope.$watch(function() {
                        return spinner.get();
                    }, function(status) {
                        scope.status = status;
                    });
                }
            };
        }]);
})();