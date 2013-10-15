define(['angular'], function(angular) {
    'use strict';

    return ['$scope',
    	function($scope) {

            $scope.widgets = [
                {
                    name:'World Clock', 
                    row:1, col:1, sizex:1, sizey:1, 
                    icon: "time",
                    template : "scripts/superdesk/dashboard/views/widgets/widget-worldclock.html",
                    class : "world-clock"
                },
                {
                    name:'Perfect Dash', 
                    row:1, col:2, sizex:1, sizey:2, 
                    icon: "leaf",
                    template: "scripts/superdesk/dashboard/views/widgets/widget-default.html",
                    class : "default"
                },
                {
                    name:'Default Widget', 
                    row:2, col:1, sizex:1, sizey:1, 
                    icon: "leaf",
                    template: "scripts/superdesk/dashboard/views/widgets/widget-default.html",
                    class : "default"
                },
                {
                    name:'Widget Cool', 
                    row:1, col:3, sizex:2, sizey:1, 
                    icon: "leaf",
                    template: "scripts/superdesk/dashboard/views/widgets/widget-default.html",
                    class : "default"
                },
                {
                    name:'DashDash', 
                    row:2, col:3, sizex:1, sizey:1, 
                    icon: "leaf",
                    template: "scripts/superdesk/dashboard/views/widgets/widget-default.html",
                    class : "default"
                }
                
            ];
    }];
});
