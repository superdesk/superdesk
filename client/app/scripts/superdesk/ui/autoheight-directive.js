define([
    'angular'
], function(angular) {
    'use strict';

    /**
     * Gives auto height while typing on textarea elements
     *
     * Usage:
     * <div sd-auto-height></div>
     *
     * Source:
     * https://github.com/monospaced/angular-elastic/blob/master/elastic.js
     *
     */
    return ['$window', function($window) {
            return {
                require: 'ngModel',
                restrict: 'A, C',
                link: function(scope, element, attrs, ngModel) {

                    // cache a reference to the DOM element
                    var ta = element[0],
                        $ta = element;

                    // ensure the element is a textarea, and browser is capable
                    if (ta.nodeName !== 'TEXTAREA' || !$window.getComputedStyle) {
                        return;
                    }

                    // set these properties before measuring dimensions
                    $ta.css({
                        'overflow': 'hidden',
                        'overflow-y': 'hidden',
                        'word-wrap': 'break-word'
                    });

                    // force text reflow
                    var text = ta.value;
                    ta.value = '';
                    ta.value = text;

                    var $win = angular.element($window),
                        mirrorStyle,
                        mirrorStyle_basic = 'position: absolute; top: -999px; right: auto; bottom: auto; left: 0 ;' +
                                      'overflow: hidden; -webkit-box-sizing: content-box;' +
                                      '-moz-box-sizing: content-box; box-sizing: content-box;' +
                                      'min-height: 0 !important; height: 0 !important; padding: 0;' +
                                      'word-wrap: break-word; border: 0;',
                        $mirror = angular.element('<textarea tabindex="-1" ' +
                                                  'style="' + mirrorStyle_basic + '"/>').attr('elastic', true),
                        mirror = $mirror[0],
                        taStyle, borderBox, boxOuter, minHeightValue, heightValue,
                        minHeight, maxHeight, mirrored, active,
                        copyStyle = ['font-family',
                                     'font-size',
                                     'font-weight',
                                     'font-style',
                                     'letter-spacing',
                                     'line-height',
                                     'text-transform',
                                     'word-spacing',
                                     'text-indent'];

                    // exit if elastic already applied (or is the mirror element)
                    if ($ta.attr('elastic')) {
                        return;
                    }

                    // append mirror to the DOM
                    if (mirror.parentNode !== document.body) {
                        angular.element(document.body).append(mirror);
                    }

                    // set resize and apply elastic
                    $ta.css({
                        'resize': 'none'
                    });
                    $ta.attr('elastic', true);

                    /*
                     * methods
                     */
                    function initMirror() {
                        mirrored = ta;
                        taStyle = $window.getComputedStyle(ta);
                        borderBox = taStyle.getPropertyValue('box-sizing') === 'border-box' ||
                                  taStyle.getPropertyValue('-moz-box-sizing') === 'border-box' ||
                                  taStyle.getPropertyValue('-webkit-box-sizing') === 'border-box';
                        boxOuter = !borderBox ? {width: 0, height: 0} : {
                            width:  parseInt(taStyle.getPropertyValue('border-right-width'), 10) +
                                    parseInt(taStyle.getPropertyValue('padding-right'), 10) +
                                    parseInt(taStyle.getPropertyValue('padding-left'), 10) +
                                    parseInt(taStyle.getPropertyValue('border-left-width'), 10),
                            height: parseInt(taStyle.getPropertyValue('border-top-width'), 10) +
                                    parseInt(taStyle.getPropertyValue('padding-top'), 10) +
                                    parseInt(taStyle.getPropertyValue('padding-bottom'), 10) +
                                    parseInt(taStyle.getPropertyValue('border-bottom-width'), 10)
                        };
                        minHeightValue = parseInt(taStyle.getPropertyValue('min-height'), 10);
                        heightValue = parseInt(taStyle.getPropertyValue('height'), 10);
                        minHeight = Math.max(minHeightValue, heightValue) - boxOuter.height;
                        maxHeight = parseInt(taStyle.getPropertyValue('max-height'), 10);
                    }

                    function setMirrorStyle() {
                        taStyle = $window.getComputedStyle(ta);
                        mirrorStyle = mirrorStyle_basic;
                        angular.forEach(copyStyle, function(val) {
                            mirrorStyle += val + ':' + taStyle[val] + ';';
                        });

                        mirror.setAttribute('style', mirrorStyle);
                    }

                    function adjust() {

                        var taHeight,
                            taComputedStyleWidth,
                            mirrorHeight,
                            width,
                            overflow;

                        if (mirrored !== ta) {
                            initMirror();
                        }

                        setMirrorStyle();

                        // active flag prevents actions in function from calling adjust again
                        if (!active) {
                            active = true;

                            mirror.value = ta.value; // optional whitespace to improve animation
                            mirror.style.overflowY = ta.style.overflowY;

                            taHeight = ta.style.height === '' ? 'auto' : parseInt(ta.style.height, 10);

                            taComputedStyleWidth = $window.getComputedStyle(ta).getPropertyValue('width');

                            // ensure getComputedStyle has returned a readable 'used value' pixel width
                            if (taComputedStyleWidth.substr(taComputedStyleWidth.length - 2, 2) === 'px') {
                                // update mirror width in case the textarea width has changed
                                width = parseInt(taComputedStyleWidth, 10) - boxOuter.width;
                                mirror.style.width = width + 'px';
                            }

                            mirrorHeight = mirror.scrollHeight;

                            if (mirrorHeight > maxHeight) {
                                mirrorHeight = maxHeight;
                                overflow = 'scroll';
                            } else if (mirrorHeight < minHeight) {
                                mirrorHeight = minHeight;
                            }
                            mirrorHeight += boxOuter.height;

                            ta.style.overflowY = overflow || 'hidden';

                            if (taHeight !== mirrorHeight) {
                                ta.style.height = mirrorHeight + 'px';
                            }

                            // small delay to prevent an infinite loop
                            _.delay(function() {
                                active = false;
                            }, 1);
                        }
                    }

                    function forceAdjust() {
                        active = false;
                        adjust();
                    }

                    /*
                     * initialise
                     */

                    // listen
                    if ('onpropertychange' in ta && 'oninput' in ta) {
                        // IE9
                        ta.oninput = ta.onkeyup = adjust;
                    } else {
                        ta.oninput = adjust;
                    }

                    $win.bind('resize', forceAdjust);

                    scope.$watch(function() {
                        return ngModel.$modelValue;
                    }, function(newval, oldval) {
                        if (newval !== oldval) {
                            forceAdjust();
                        }
                    });

                    _.defer(adjust);

                    /*
                     * destroy
                     */

                    scope.$on('$destroy', function() {
                        $mirror.remove();
                        $win.unbind('resize', forceAdjust);
                    });
                }
            };
        }];
});
