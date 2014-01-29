define(['angular'], function(angular) {
    'use strict';

    return ['$scope', '$location', '$filter', 'em', 'storage', 'superdesk', 'panesService', 'workqueue',
    function($scope, $location, $filter, em, storage, superdesk, panesService, queue) {
        $scope.articles = queue.all();

        $scope.slider = {
            options : {
                from: 1,
                to: 5,
                step: 1
            }
        };

        $scope.$watch(function() {
            return $location.search()._id;
        }, function(_id) {
            $scope.item = queue.find({_id: _id}) || queue.active;
            $scope.item.place = $filter('mergeWords')($scope.item.place || []);
        });

        $scope.save = function() {
            $scope.item.place = $filter('splitWords')( $scope.item.place);
            em.save('archive', $scope.item).then(function(data) {
                _.extend($scope.item, data);
                $scope.item.place = $filter('mergeWords')( $scope.item.place);
            });
        };

        $scope.switchArticle = function(article) {
            queue.setActive(article);
            $location.search('_id', article._id);
        };

        //tabpane logic
        $scope.panes = panesService.load();

        $scope.tabpaneIsOpen = function(side) {
            return $filter('filterObject')($scope.panes, {position:side, selected: true, active:true}).length > 0;
        };

        $scope.flipActive = function(pane, side) {
            angular.forEach($filter('filterObject')($scope.panes, {position:side, selected: true, active:true}), function(value, key) {
                value.active = (value !== pane) ? false : value.active;
            });
            pane.active = !pane.active;
            panesService.save($scope.panes);
        };

    }];
});