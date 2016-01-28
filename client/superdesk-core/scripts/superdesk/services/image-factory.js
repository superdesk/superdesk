(function() {
'use strict';

/**
* Factory for creating Image objects. Allows for easier mocking in tests.
*
* @class imageFactory
*/
return angular.module('superdesk.imageFactory' , []).factory('imageFactory',
    function () {
        return {
            makeInstance: function () {
                return new Image();
            }
        };
    }
);
})();
