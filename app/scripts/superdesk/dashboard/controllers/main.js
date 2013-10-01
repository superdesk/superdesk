define(['angular'], function(angular) {
    'use strict';

    return ['$scope', 'worldclock',
    	function($scope, worldclock) {
        	$scope.wclock = worldclock;
    }];
});
