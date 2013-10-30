define(['angular', 'lodash'], function(angular, _) {
    'use strict';

    return ['$scope', '$modal', '$window', 'providerRepository', 'em', 'gettext', 'notify',
        function($scope, $modal, $window, providerRepository, em, gettext, notify) {

            providerRepository.matching({sort: ['created', 'desc'], max_results: 50}).then(function(providers) {
                $scope.providers = providers;
            });

            $scope.remove = function(provider) {
                if ($window.confirm(gettext('Are you sure you want to delete selected provider(s)?'))) {
                    em.remove(provider).then(function() {
                        _.remove($scope.providers._items, provider);
                        notify.success(gettext('Provider deleted.'), 3000);
                    });
                }
            };

            $scope.edit = function(provider) {
		        var modal = $modal.open({
                    templateUrl : 'scripts/superdesk/general-settings/views/addSourceModal.html',
                    controller : 'AddSourceModalCtrl',
                    windowClass : 'addSource',
                    resolve: {
                        provider: function() {
                            return provider ? provider : {};
                        }
                    }
		        });

                modal.result.then(function(newProvider) {
                    notify.success(gettext('Provider saved!'), 3000);
                    if (provider !== newProvider) {
                        $scope.providers._items.unshift(newProvider);
                    }
                });
		    };
        }];
});