define(['lodash'], function(_) {
    'use strict';

    AuthoringController.$inject = ['$scope', 'api', '$location', 'workqueue'];
    function AuthoringController($scope, api, $location, workqueue) {

    	$scope.editItem = null;
    	var item = null;

        $scope.workqueue = workqueue.all();

        $scope.$watch(function() {
            return $location.search()._id;
        }, function(_id) {
            item = workqueue.find({_id: _id}) || workqueue.active;
            $scope.editItem = _.create(item);
        });

        $scope.switchArticle = function(article) {
            workqueue.update($scope.editItem);
            workqueue.setActive(article);
            $location.search('_id', article._id);
        };

    	$scope.save = function() {
    		api.archive.save(item, $scope.editItem).then(function() {
    			//success
    		}, function(response) {
    			//error
    		});
    	};

    }

    return AuthoringController;

});
