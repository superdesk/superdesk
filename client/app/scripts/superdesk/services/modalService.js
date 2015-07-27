define(['angular'], function(angular) {
    'use strict';

    return angular.module('superdesk.services.modal', ['ui.bootstrap', 'superdesk.asset'])
        .service('modal', ['$q', '$modal', '$sce', 'asset', function($q, $modal, $sce, asset) {
            this.confirm = function(bodyText, headerText, okText, cancelText, additionalCancelText) {
                headerText = headerText || gettext('Confirm');
                okText = okText || gettext('OK');
                cancelText = cancelText != null ? cancelText : gettext('Cancel');
                additionalCancelText = additionalCancelText != null ? additionalCancelText : null;
                var delay = $q.defer();

                $modal.open({
                    templateUrl: asset.templateUrl('superdesk/views/confirmation-modal.html'),
                    controller: ['$scope', '$modalInstance', function($scope, $modalInstance) {
                        $scope.headerText = $sce.trustAsHtml(headerText);
                        $scope.bodyText = $sce.trustAsHtml(bodyText);
                        $scope.okText = okText;
                        $scope.cancelText = cancelText;
                        $scope.additionalCancelText = additionalCancelText;

                        $scope.ok = function() {
                            delay.resolve(true);
                            $modalInstance.close();
                        };

                        $scope.cancel = function() {
                            delay.reject();
                            $modalInstance.dismiss();
                        };

                        $scope.additionalCancel = function() {
                            $modalInstance.dismiss();
                        };

                        $scope.close = function() {
                            $modalInstance.dismiss();
                        };
                    }]
                });

                return delay.promise;
            };

        }])
        .directive('sdModal', ['$document', function($document) {

            return {
                template: [
                    '<div class="modal">',
                    '<div class="modal-dialog" ng-if="model"><div class="modal-content" ng-transclude></div></div>',
                    '</div>'].join(''),
                transclude: true,
                scope: {
                    model: '='
                },
                link: function(scope, element, attrs) {

                    var content, _initialized = false;

                    scope.$watch('model', function() {
                        if (scope.model) {
                            if (!_initialized) {
                                content = element.children();
                                content.addClass(element.attr('class'));
                                content.appendTo($document.find('body'));
                                _initialized = true;
                            }
                            content.modal('show');
                        } else {
                            if (initialized()) {
                                content.modal('hide');
                            }
                        }
                    });

                    $(document).on('hidden.bs.modal', '.modal', function () {
                        scope.model = false;
                        scope.$evalAsync();
                    });

                    function initialized() {
                        return _initialized && content;
                    }

                    scope.$on('$destroy', function() {
                        if (initialized()) {
                            content.modal('hide');
                            content.remove();
                        }
                        angular.element(document.body).find('.modal-backdrop').remove();
                    });
                }
            };
        }]);
});
