define(['angular'], function(angular) {
    'use strict';

    return ['$scope', 'server', '$location', 'item', 'ItemService', 'storage', 'articles',
    function($scope, server, $location, item, ItemService, storage, articles) {

        $scope.item = item;
        var inprogress = storage.getItem('collection:inprogress') || {};

        var saveInprogress = function() {
            storage.setItem('collection:inprogress',inprogress,false);
        };

        $scope.articles = articles;

        $scope.save = function(item) {
            ItemService.update(item);
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

    }];
});