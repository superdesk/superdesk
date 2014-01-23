define(['angular'], function(angular) {
    'use strict';

    return ['$scope', 'superdesk', 'locationParams', 'keyboardManager', 'storage', 'em',
    function($scope, superdesk, locationParams, keyboardManager, storage, em) {
        var items = $scope.items = superdesk.data('ingest', {
            sort: ['firstcreated', 'desc'],
            filters: ['provider'],
            max_results: 25
        });

        $scope.inprogress =  storage.getItem('collection:inprogress') || { all : [], opened : [], active : null };

        var putInProgress = function(item_id, setActive) {

            if (_.indexOf($scope.inprogress.all, item_id) === -1) {
                $scope.inprogress.all.push(item_id);
            }
            if (_.indexOf($scope.inprogress.opened, item_id) === -1) {
                $scope.inprogress.opened.push(item_id);
            }
            if (setActive === true) {
                $scope.inprogress.active = item_id;
            }
            storage.setItem('collection:inprogress', $scope.inprogress, false);
        };
        
        $scope.context = false;     //status of context menu (open or not)
        $scope.contextMenu = [
            {
                title : 'Article',
                action : 'fetch-article'
            },
            {
                title : 'Factbox',
                action : 'fetch-factbox'
            },
            {
                title : 'Sidebar',
                action : 'fetch-sidebar'
            },
            {
                title : 'Blank article',
                action : 'fetch-blank'
            }
        ];
        
        var contextAction = function(action) {
            switch (action) {
                case 'fetch-article' :
                    $scope.archive();
                    break;
                case 'fetch-factbox' :
                    break;
                case 'fetch-sidebar' :
                    break;
                case 'fetch-blank' :
                    break;
            }
        };

        $scope.selectedContext = 0;

        $scope.selectContext = function(index) {
            //on mouseenter
            $scope.selectedContext = index;
        };

        keyboardManager.bind('enter', function() {
            $scope.selectAction();
        }, {
            'inputDisabled': true
        });

        keyboardManager.bind('esc', function() {
            if ($scope.context) {
                $scope.context = false ;
            }
        });

        $scope.selectAction = function() {
            if ($scope.context) {
                //select context action if context menu is open
                contextAction($scope.contextMenu[$scope.selectedContext].action);
                $scope.selectedContext = 0;
            }
            //open/close context menu
            $scope.context = !$scope.context ;
        };

        $scope.fetch = function(index) {
            //preview
            $scope.preview(items._items[index],index);

            //open context menu if not already
            $scope.context = true;
        };

        $scope.preview = function(item, index) {
            $scope.context = false;
            if (item !== undefined) {
                $scope.previewItem = item;
                $scope.previewSingle = item;

                if (item.type === 'composite') {
                    $scope.previewSingle = null;
                    $scope.previewItem.packageRefs = _.where(item.groups,{'id':'main'})[0].refs;
                }
            }
        };

        $scope.openEditor = function(item_id) {
            //remember url params in session storage
            if (item_id !== undefined) {
                putInProgress(item_id, true);
                openItem(item_id);
            }
            else if ($scope.inprogress.active !== null) {
                openItem($scope.inprogress.active);
            }
            else if ($scope.inprogress.opened.length) {
                putInProgress($scope.inprogress.opened[0], true);
                openItem($scope.inprogress.opened[0]);
            }
        };
    }];
});
