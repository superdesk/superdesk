define(['angular'], function(angular) {
    'use strict';

    return ['$scope', 'items', 'em', '$location', 'locationParams', 'keyboardManager', 'storage',
    function($scope, items, em, $location, locationParams, keyboardManager, storage) {

        $scope.items = items;
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
        var previousContext = function() {
            if ($scope.selectedContext>0) {
                $scope.selectedContext--;
            }
        };
        var nextContext = function() {
            if ($scope.selectedContext<($scope.contextMenu.length-1)) {
                $scope.selectedContext++;
            }
        };
        $scope.selectContext = function(index) {
            //on mouseenter
            $scope.selectedContext = index;
        };

        $scope.selectedItemIndex = -1;
        var previousitem = function() {
            if ($scope.selectedItemIndex>0) {
                $scope.selectedItemIndex--;
            }
            $scope.preview(items._items[$scope.selectedItemIndex],$scope.selectedItemIndex);
        };
        var nextitem = function() {
            if ($scope.selectedItemIndex<(items._items.length-1)) {
                $scope.selectedItemIndex++;
            }
            $scope.preview(items._items[$scope.selectedItemIndex],$scope.selectedItemIndex);
        };
        

        keyboardManager.bind('up', function() {
            if ($scope.context) {
                previousContext();
            }
            else {
                previousitem();
            }
        }, {
            'inputDisabled': true
        });
        keyboardManager.bind('down', function() {
            if ($scope.context) {
                nextContext();
            }
            else {
                nextitem();
            }
        }, {
            'inputDisabled': true
        });

        keyboardManager.bind('ctrl+a', function() {
            $scope.archive();
        });

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
                $scope.selectedItemIndex = index;
                $scope.previewItem = item;
                $scope.previewSingle = item;

                if (item.type === 'composite') {
                    $scope.previewSingle = null;
                    $scope.previewItem.packageRefs = _.where(item.groups,{'id':'main'})[0].refs;
                }
            }
        };

        $scope.archive = function() {
            var item = items._items[$scope.selectedItemIndex];
            if (item.archived === undefined) {
                em.create('archive', item).then(function(data) {
                    delete item.archiving;
                    item.archived = data.archived;
                    putInProgress(data._id, false);
                });
                item.archiving = true;
            }
        };

        nextitem(); //initialy select(focus on) first item on ingest page 

        $scope.openEditor = function(item_id) {
            //remember url params in session storage
            storage.setItem('ingest:navigation-params', $location.url(), false);
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

        var openItem = function(item_id) {
            $location.url('/article/'+item_id);
        };


        if (locationParams.get('id')) {
            var item = _.find($scope.items._items, {_id: locationParams.get('id')});
            if (item) {
                $scope.preview(item);
            }
        }
        

    }];
});
