define(['lodash'], function(_) {
    'use strict';

    AuthoringController.$inject = ['$scope', 'api', '$location', 'workqueue', 'notify', 'gettext'];
    function AuthoringController($scope, api, $location, workqueue, notify, gettext) {

    	$scope.item = null;
    	var _item = null;

        $scope.workqueue = workqueue.all();

        $scope.$watch(function() {
            return $location.search()._id;
        }, function(_id) {
            if (_id) {
                _item = workqueue.find({_id: _id}) || workqueue.active;
                $scope.item = _.create(_item);
                workqueue.setActive(_item);
            } else {
                $scope.item = null;
                _item = null;
            }
        });

        $scope.create = function() {
            var temp = {
                type: 'text',
                guid: 'item:' + Math.random()
            };
            api.archive.save(temp, {}).then(function(newItem) {
                workqueue.add(newItem);
                $scope.switchArticle(newItem);
            }, function(response) {
                notify.error(gettext('Error. Item not created.'));
            });
        };

        $scope.switchArticle = function(article) {
            workqueue.update($scope.item);
            workqueue.setActive(article);
            $location.search({_id: article._id});
        };

    	$scope.save = function() {
    		api.archive.save(_item, $scope.item).then(function(res) {
                workqueue.update($scope.item);
    		}, function(response) {
    			notify.error(gettext('Error. Item not updated.'));
    		});
    	};

        $scope.close = function() {
            workqueue.remove(_item);
            $location.search('_id', workqueue.getActive());
        };

    }

    return AuthoringController;

});
