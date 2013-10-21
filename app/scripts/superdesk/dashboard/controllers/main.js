define(['angular'], function(){
    'use strict';

    return ['$scope', 'widgetList', '$timeout',
        function($scope, widgetList, $timeout){ 

            $scope.allWidgets = [];
            $scope.widgets = [];

            widgetList.get(function(data){
                $scope.allWidgets = data.allWidgets;
                $scope.widgets = data.userWidgets;
            });

            $scope.addWidget = function(widget) {
                widget.row = 1;
                widget.col = 1;
                $scope.widgets.push(widget);
                if (!$scope.editmode) $scope.enableDragging();
            };


            


        }];
});
