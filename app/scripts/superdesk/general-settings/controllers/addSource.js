define(['angular'], function(angular){
    'use strict';

	angular.module('superdesk.generalSettings.controllers', [])
	.controller('AddSourceModalCtrl',
		function ($scope, $modalInstance) {
			$scope.closeModal = function () {
				$modalInstance.dismiss('cancel');
			};
        });
});
