define(['angular'], function(angular) {
    'use strict';

    return ['$scope', '$location', '$filter','item', 'em', 'storage', 'articles', 'superdesk',
    function($scope, $location, $filter, item, em, storage, articles, superdesk) {

        $scope.item = item;
        var inprogress = storage.getItem('collection:inprogress') || {};

        var saveInprogress = function() {
            storage.setItem('collection:inprogress',inprogress,false);
        };

        $scope.articles = articles;

        $scope.save = function(item) {
            em.save('ingest', item);
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
        $scope.panes = _.map(superdesk.panes);

        $scope.tabpaneIsOpen = function(side) {
            return $filter('filter')($scope.panes, {position:side, selected: true, active:true}).length > 0;
        }

        $scope.flipActive = function(pane, side) {
            angular.forEach($filter('filter')($scope.panes, {position:side, selected: true, active:true}), function(value, key) {
                value.active = (value != pane) ? false : value.active;
            });
            pane.active = !pane.active;
        }

        

    }];
});