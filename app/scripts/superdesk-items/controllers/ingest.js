define(['angular'], function(angular) {
    'use strict';

    return ['$scope', 'items', 'em', 'locationParams', 'keyboardManager',
    function($scope, items, em, locationParams, keyboardManager) {

        $scope.items = items;
        
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
        
        $scope.contextAction = function(action) {
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
            //on mouse enter
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
            if ($scope.context) {
                $scope.contextAction($scope.contextMenu[$scope.selectedContext].action);
                $scope.selectedContext = 0;
            }
            $scope.context = !$scope.context ;
        }, {
            'inputDisabled': true
        });

        keyboardManager.bind('esc', function() {
            if ($scope.context) {
                $scope.context = false ;
            }
        });



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
            em.create('archive', item).then(function(data) {
                delete item.archiving;
                _.extend(item,data);
            });
            item.archiving = true;
        };

        nextitem();

        if (locationParams.get('id')) {
            var item = _.find($scope.items._items, {_id: locationParams.get('id')});
            if (item) {
                $scope.preview(item);
            }
        }


    }];
});
