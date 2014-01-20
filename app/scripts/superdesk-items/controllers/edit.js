define(['angular'], function(angular) {
    'use strict';

    return ['$scope', '$location', '$filter','item', 'em', 'storage', 'articles', 'superdesk', 'panesService',
    function($scope, $location, $filter, item, em, storage, articles, superdesk, panesService) {

        $scope.item = item;
        $scope.item.place = $filter('mergeWords')($scope.item.place);

        var inprogress = storage.getItem('collection:inprogress') || {};

        var saveInprogress = function() {
            storage.setItem('collection:inprogress',inprogress,false);
        };

        $scope.articles = articles;

        $scope.slider = {
            options : {
                from: 1,
                to: 5,
                step: 1
            }
        };

        $scope.save = function() {
            $scope.item.place = $filter('splitWords')( $scope.item.place);
            em.save('ingest', $scope.item).then(function(data) {
                _.extend($scope.item,data);
                $scope.item.place = $filter('mergeWords')( $scope.item.place);
            });
            
        };

        $scope.close = function() {
            $location.path('/');
        };

        $scope.backToIngest = function() {
            var ingest = storage.getItem('ingest:navigation-params');
            if (ingest !== null) {
                $location.url(ingest);
            }
        };

        $scope.switchArticle = function(id) {
            inprogress.active = id;
            saveInprogress();
            $location.url('/article/'+id);
        };

        $scope.closeArticle = function() {
            //close this
            inprogress.opened = _.without(inprogress.opened,$scope.item._id);
            inprogress.active = null;
            saveInprogress();

            //if there is at least one more item in opened array bring it
            if (inprogress.opened.length > 0) {
                $scope.switchArticle(inprogress.opened[0]);
            }
            else {
                $location.url('/article/');
            }
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