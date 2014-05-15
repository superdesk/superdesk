define([
    'jquery',
    'angular'
], function($, angular) {
    'use strict';

        /**
         * Gives top shadow for scroll elements
         *
         * Usage:
         * <div sd-shadow></div>
         *
         */
        return [ '$timeout', function($timeout) {
            return {
                link: function(scope, element, attrs) {

                    $timeout(function() {
                        var el = $(element);
                        var shadow = $('<div class="scroll-shadow"></div>');
                        shadow.css({
                                top: el.offset().top,
                                left: el.offset().left,
                                width: el.outerWidth()
                            });
                        $('body').append(shadow);

                        el.scroll(function() {
                            if ($(this).scrollTop() > 0) {
                                shadow.addClass('shadow');
                            } else {
                                shadow.removeClass('shadow');
                            }
                        });
                    }, 500);
                }
            };
        }];
});
