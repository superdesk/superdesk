/**
 * This file is part of Superdesk.
 *
 * Copyright 2013, 2014 Sourcefabric z.u. and contributors.
 *
 * For the full copyright and license information, please see the
 * AUTHORS and LICENSE files distributed with this source code, or
 * at https://www.sourcefabric.org/superdesk/license
 */

(function() {

    'use strict';

    var app = angular.module('superdesk.docs', []);

    MainDocsView.$inject = ['$location', '$anchorScroll'];
    function MainDocsView($location, $anchorScroll) {
        return {
            templateUrl: '/docs/views/main.html',
            link: function(scope, elem, attrs) {
                scope.scrollTo = function(id) {
                    $location.hash(id);
                    $anchorScroll();
                };

                //Modals
                scope.modalActive = false;

                scope.openModal = function() {
                    scope.modalActive = true;
                };

                scope.closeModal = function() {
                    scope.modalActive = false;
                };

                //Select boxes
                scope.opts = ['Serbia', 'Czech Republic', 'Germany', 'Australia'];

                //Typeahead
                scope.taTerms = ['Serbia', 'Czech Republic', 'Germany', 'Australia', 'Canada', 'Russia', 'Italy', 'Egypt', 'China'];
                scope.taSelected = null;
                scope.taItems = [];

                scope.taSearch = function(term) {
                    scope.taItems = _.filter(scope.taTerms, function(t) {
                        return t.toLowerCase().indexOf(term.toLowerCase()) !== -1;
                    });
                    return scope.taItems;
                };

                scope.taSelect = function(term) {
                    scope.taSelected = term;
                };

                //datepicker
                scope.dateNow = moment().utc().format();

                //timepicker
                scope.timeNow = moment().utc().format('HH:mm:ss');
            }
        };
    }

    app.directive('sdDocs', MainDocsView);
    app.directive('prettyprint', function() {
        return {
            restrict: 'C',
            link: function postLink(scope, element, attrs) {

                //remove leading whitespaces
                var str = element[0].innerHTML;
                var pos = 0; var sum = 0;
                while (str.charCodeAt(pos) === 32) {
                    sum = sum + 1;
                    pos = pos + 1;
                }
                var pattern = '\\s{' + sum + '}';
                var spaces = new RegExp(pattern, 'g');
                element[0].innerHTML = str.replace(spaces, '\n');

                //remove ng-non-bindable from code
                element.find('[ng-non-bindable=""]').each(function(i, val) {
                    $(val).removeAttr('ng-non-bindable');
                });

                var langExtension = attrs['class'].match(/\blang(?:uage)?-([\w.]+)(?!\S)/);
                if (langExtension) {
                    langExtension = langExtension[1];
                }
                element.html(window.prettyPrintOne(_.escape(element.html()), langExtension, true));
            }

        };
    });

    return app;

})();
