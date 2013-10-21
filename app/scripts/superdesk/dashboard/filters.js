define([
    'jquery',
    'angular'
], function($, angular) {
    angular.module('superdesk.dashboard.filters', []).
        filter('wcodeFilter', function() {
          return function(input, values) {
            var out = [];
              for (var i = 0; i < input.length; i++){
                var flag = false;
                for (var j=0; j < values.length; j++) {
                    if(input[i].wcode == values[j].wcode) {
                        flag = true; break;
                    }
                }
                if (!flag) { out.push(input[i]); }
              }      
            return out;
          };
        });
});