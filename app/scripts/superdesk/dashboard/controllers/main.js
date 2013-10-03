define(['angular'], function(angular) {
    'use strict';

    return ['$scope',
    	function($scope) {

        	$scope.widget = {
        		"worldclock": {
        			"name"	: "World Clock",
        			"icon"  : "time"
        		},
        		"default"	: {
        			"name"	: "Default Widget",
        			"icon"  : "leaf"
        		}
        	}


    }];
});
