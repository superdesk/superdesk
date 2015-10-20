define([
    'angular',
    'require',
    'moment',
    './autoheight-directive'
], function(angular, require, moment) {
    'use strict';

    /**
     * Gives toggle functionality to the box
     *
     * Usage:
     * <div sd-toggle-box data-title="Some title" data-open="true" data-icon="list"></div>
     *
     */
    function ToggleBoxDirective() {
        return {
            templateUrl: 'scripts/superdesk/ui/views/toggle-box.html',
            transclude: true,
            scope: true,
            link: function($scope, element, attrs) {
                $scope.title = attrs.title;
                $scope.isOpen = attrs.open === 'true';
                $scope.icon = attrs.icon;
                $scope.mode = attrs.mode;
                $scope.style = attrs.style;
                $scope.toggleModule = function() {
                    $scope.isOpen = !$scope.isOpen;
                };
            }
        };
    }

    /**
     * Gives top shadow for scroll elements
     *
     * Usage:
     * <div sd-shadow></div>
     */
    ShadowDirective.$inject = ['$timeout'];
    function ShadowDirective($timeout) {
        return {
            link: function(scope, element, attrs) {

                element.addClass('shadow-list-holder');

                function shadowTimeout() {
                    var shadow = angular.element('<div class="scroll-shadow"><div class="inner"></div></div>');
                    element.parent().prepend(shadow);
                    element.on('scroll', function scroll() {
                        if ($(this).scrollTop() > 0) {
                            shadow.addClass('shadow');
                        } else {
                            shadow.removeClass('shadow');
                        }
                    });
                }

                scope.$on('$destroy', function() {
                    element.off('scroll');
                });

                $timeout(shadowTimeout, 1, false);
            }
        };
    }

    /**
     * Convert newline charachter from text into given html element (default <br/>)
     *
     * Usage:
     * <div data-html="text | nl2el"></div>
     * or
     * <div data-html="text | nl2el:'</p><p>'"></div> for specific replace element
     */
    function NewlineToElement() {
        return function(input, el) {
            return input.replace(/(?:\r\n|\r|\n)/g, el || '<br/>');
        };
    }

    /**
     * Handle all wizards used in UI
     *
     */
    WizardHandlerFactory.$inject = [];
    function WizardHandlerFactory() {

        var service = {};
        var wizards = {};

        service.defaultName = 'defaultWizard';

        service.addWizard = function(name, wizard) {
            wizards[name] = wizard;
        };

        service.removeWizard = function(name) {
            delete wizards[name];
        };

        service.wizard = function(name) {
            var nameToUse = name || service.defaultName;
            return wizards[nameToUse];
        };

        return service;
    }

    WizardDirective.$inject = [];
    function WizardDirective() {
        return {
            templateUrl: 'scripts/superdesk/ui/views/wizard.html',
            scope: {
                currentStep: '=',
                finish: '&',
                name: '@'
            },
            transclude: true,
            controller: ['$scope', '$element', 'WizardHandler', function($scope, element, WizardHandler) {

                WizardHandler.addWizard($scope.name || WizardHandler.defaultName, this);
                $scope.$on('$destroy', function() {
                    WizardHandler.removeWizard($scope.name || WizardHandler.defaultName);
                });

                $scope.selectedStep = null;
                $scope.steps = [];

                var stopWatch;
                this.addStep = function(step) {
                    $scope.steps.push(step);

                    if (!stopWatch) {
                        stopWatch = $scope.$watch('currentStep', function(stepCode) {
                            if (stepCode && (($scope.selectedStep && $scope.selectedStep.code !== stepCode) || !$scope.selectedStep)) {
                                $scope.goTo(_.findWhere($scope.steps, {code: stepCode}));
                            }
                        });
                    }
                };

                function unselectAll() {
                    _.each($scope.steps, function (step) {
                        step.selected = false;
                    });
                    $scope.selectedStep = null;
                }

                $scope.goTo = function(step) {
                    unselectAll();
                    $scope.selectedStep = step;
                    if (!_.isUndefined($scope.currentStep)) {
                        $scope.currentStep = step.code;
                    }
                    step.selected = true;
                };

                this.goTo = function(step) {
                    var stepTo;
                    if (_.isNumber(step)) {
                        stepTo = $scope.steps[step];
                    } else {
                        stepTo = _.findWhere($scope.steps, {code: step});
                    }
                    $scope.goTo(stepTo);
                };

                this.next = function() {
                    var index = _.indexOf($scope.steps , $scope.selectedStep);
                    if (index === $scope.steps.length - 1) {
                        this.finish();
                    } else {
                        $scope.goTo($scope.steps[index + 1]);
                    }
                };

                this.previous = function() {
                    var index = _.indexOf($scope.steps , $scope.selectedStep);
                    $scope.goTo($scope.steps[index - 1]);
                };

                this.finish = function() {
                    if ($scope.finish) {
                        $scope.finish();
                    }
                };
            }]
        };
    }

    WizardStepDirective.$inject = [];
    function WizardStepDirective() {
        return {
            templateUrl: 'scripts/superdesk/ui/views/wizardStep.html',
            scope: {
                title: '@',
                code: '@',
                disabled: '='
            },
            transclude: true,
            require: '^sdWizard',
            link: function($scope, element, attrs, wizard) {
                wizard.addStep($scope);
            }
        };
    }

    CreateButtonDirective.$inject = [];
    function CreateButtonDirective() {
        return {
            restrict: 'C',
            template: '<i class="svg-icon-plus"></i><span class="circle"></span>'
        };
    }

    AutofocusDirective.$inject = [];
    function AutofocusDirective() {
        return {
            link: function(scope, element) {
                _.defer (function() {
                    element.focus();
                });
            }
        };
    }

    AutoexpandDirective.$inject = [];
    function AutoexpandDirective() {
        return {
            link: function(scope, element) {

                var _minHeight = element.outerHeight();

                function resize() {
                    var e = element[0];
                    var vlen = e.value.length;
                    if (vlen !== e.valLength) {
                        if (vlen < e.valLength) {
                            e.style.height = '0px';
                        }
                        var h = Math.max(_minHeight, e.scrollHeight);

                        e.style.overflow = (e.scrollHeight > h ? 'auto' : 'hidden');
                        e.style.height = h + 1 + 'px';

                        e.valLength = vlen;
                    }
                }

                resize();

                element.on('keyup change', function() {
                    resize();
                });

            }
        };
    }

    DropdownPositionDirective.$inject = ['$document'];
    function DropdownPositionDirective($document) {
        return {
            link: function(scope, element) {

                var tolerance = 300,
                    isRightOriented = null,
                    isInlineOriented = null,
                    menu = null;

                element.bind('click', function(event) {

                    if (menu === null) {
                        checkOrientation();
                    }

                    if (closeToBottom(event)) {
                        element.addClass('dropup');
                    } else {
                        element.removeClass('dropup');
                    }

                    if (isRightOriented) {
                        if (closeToLeft(event)) {
                            menu.removeClass('pull-right');
                        } else {
                            menu.addClass('pull-right');
                        }

                        if (closeToRight(event)) {
                            menu.addClass('pull-right');
                        } else {
                            menu.removeClass('pull-right');
                        }
                    }

                    if (isInlineOriented) {
                        if (closeToLeft(event)) {
                            element.removeClass('dropleft').addClass('dropright');
                        } else {
                            element.addClass('dropleft').removeClass('dropright');
                        }

                        if (closeToRight(event)) {
                            element.removeClass('dropright').addClass('dropleft');
                        } else {
                            element.addClass('dropright').removeClass('dropleft');
                        }
                    }
                });

                function checkOrientation() {
                    menu = element.children('.dropdown-menu');
                    isRightOriented = menu.hasClass('pull-right');
                    isInlineOriented = element.hasClass('dropright') || element.hasClass('dropleft');
                }

                function closeToBottom(e) {
                    var docHeight = $document.height();
                    return e.pageY > docHeight - tolerance;
                }

                function closeToLeft(e) {
                    return e.pageX < tolerance;
                }

                function closeToRight(e) {
                    var docWidth = $document.width();
                    return (docWidth - e.pageX) < tolerance;
                }
            }
        };
    }

    DropdownPositionRightDirective.$inject = ['$position'];
    /**
     * Correct dropdown menu position to be right aligned
     * with dots-vertical icon.
     */
    function DropdownPositionRightDirective($position) {
        return {
            require: 'dropdown',
            link: function(scope, elem, attrs, dropdown) {
                var icon = elem.find('.icon-dots-vertical');
                // ported from bootstrap 0.13.1
                scope.$watch(dropdown.isOpen, function(isOpen) {
                    if (isOpen) {
                        var pos = $position.positionElements(
                            icon,
                            dropdown.dropdownMenu,
                            'bottom-right',
                            true
                        );

                        var css = {
                            top: pos.top + 'px',
                            display: isOpen ? 'block' : 'none',
                            opacity: '1'
                        };

                        css.left = 'auto';
                        css.right = Math.max(5, window.innerWidth - pos.left);

                        dropdown.dropdownMenu.css({opacity: '0'}); // avoid flickering

                        scope.$applyAsync(function () {
                            dropdown.dropdownMenu.css(css);

                            /*
                             * Calculate if there is enough space for showing after the icon
                             * if not, show it above the icon
                             */
                            var windowHeight = window.innerHeight - 30, //Subracting 30 is for submenu bar
                                dropdownHeight = dropdown.dropdownMenu.outerHeight();

                            if ((windowHeight - pos.top) < dropdownHeight) {
                                if ((pos.top - 110) < dropdownHeight) { //Substracting 110 is for topmenu and submenu bar
                                    css = {
                                        top: '110px',
                                        right: css.right + 30
                                        // Addition 30 so the drodpown would not overlap icon
                                    };
                                } else {
                                    css.top = pos.top - dropdownHeight - icon.outerHeight() - 15;
                                    //Subtracting 15 so the dropdown is not stick to the icon
                                }

                                dropdown.dropdownMenu.css({
                                    top: css.top,
                                    right: css.right
                                });
                            }
                        });
                    }
                });
            }
        };
    }

    PopupService.$inject = ['$document'];
    function PopupService($document) {
        var service = {};

        service.position = function(width, height, target) {
            //taking care of screen size and responsiveness
            var tolerance = 10;
            var elOffset = target.offset();
            var elHeight = target.outerHeight();
            var docHeight = $document.height();
            var docWidth = $document.width();

            var position = {top: 0, left:0};

            if ((elOffset.top + elHeight + height + tolerance) > docHeight) {
                position.top = elOffset.top - height;
            } else {
                position.top = elOffset.top + elHeight;
            }

            if ((elOffset.left + width + tolerance) > docWidth) {
                position.left = docWidth - tolerance - width;
            } else {
                position.left = elOffset.left;
            }
            return position;
        };

        return service;
    }

    function DatepickerWrapper() {
        return {
            transclude: true,
            templateUrl: 'scripts/superdesk/ui/views/datepicker-wrapper.html',
            link:function (scope, element) {
                element.bind('click', function(event) {
                    event.preventDefault();
                    event.stopPropagation();
                });
            }
        };
    }

    /**
     * Datepicker directive
     *
     * Expects: UTC string or UTC time object
     * Returns: UTC string if input is valid or NULL if it's not
     *
     * Usage:
     * <div sd-datepicker ng-model="date"></div>
     *
     * More improvements TODO:
     *     > accept min and max date
     *     > date format as parameter
     *     > keep time not reseting it
     */

    function DatepickerDirective() {
        return {
            scope: {
                dt: '=ngModel',
                disabled: '=ngDisabled'
            },
            templateUrl: 'scripts/superdesk/ui/views/sd-datepicker.html'
        };
    }

    DatepickerInnerDirective.$inject = ['$compile', '$document', 'popupService', 'datetimeHelper'];
    function DatepickerInnerDirective($compile, $document, popupService, datetimeHelper) {
        var popupTpl =
        '<div sd-datepicker-wrapper ng-model="date" ng-change="dateSelection()">' +
            '<div datepicker format-day="d" show-weeks="false"></div>' +
        '</div>';

        return {
            require: 'ngModel',
            scope: {
                open: '=opened'
            },
            link: function (scope, element, attrs, ctrl) {

                var VIEW_FORMAT = 'DD/MM/YYYY',
                    ESC = 27,
                    DOWN_ARROW = 40;

                var popup = angular.element(popupTpl);

                ctrl.$parsers.unshift(function parseDate(viewValue) {

                    if (!viewValue) {
                        ctrl.$setValidity('date', true);
                        return null;
                    } else {
                        if (viewValue.dpdate) {
                            ctrl.$setValidity('date', true);
                            return moment.utc(viewValue.dpdate).format();
                        } else {
                            if (datetimeHelper.isValidDate(viewValue)) {
                                if (moment(viewValue, VIEW_FORMAT).isValid()) {
                                    ctrl.$setValidity('date', true);
                                    return moment(viewValue, VIEW_FORMAT).utc().format();
                                } else {
                                    //value cannot be converted
                                    ctrl.$setValidity('date', false);
                                    return null;
                                }
                            } else {
                                //input is not valid
                                ctrl.$setValidity('date', false);
                                return null;
                            }
                        }
                    }
                });

                scope.dateSelection = function(dt) {
                    if (angular.isDefined(dt)) {
                        //if one of predefined dates is selected (today, tomorrow...)
                        scope.date = dt;
                    }
                    ctrl.$setViewValue({dpdate: scope.date, viewdate: moment(scope.date).format(VIEW_FORMAT)});
                    ctrl.$render();
                    scope.close();
                };

                //select one of predefined dates
                scope.select = function(offset) {
                    var day = moment().startOf('day').add(offset, 'days');
                    scope.dateSelection(day);
                };

                ctrl.$render = function() {
                    element.val(ctrl.$viewValue.viewdate);  //set the view
                    scope.date = ctrl.$viewValue.dpdate;    //set datepicker model
                };

                //handle model changes
                ctrl.$formatters.unshift(function dateFormatter(modelValue) {

                    var dpdate,
                        viewdate = 'Invalid Date';

                    if (modelValue) {
                        if (moment(modelValue).isValid()) {
                            //formatter pass fine
                            dpdate = moment.utc(modelValue).toDate();
                            viewdate = moment(modelValue).format(VIEW_FORMAT);
                        }
                    } else {
                        viewdate = '';
                    }

                    return {
                        dpdate: dpdate,
                        viewdate: viewdate
                    };
                });

                var closeOnClick = function(event) {
                    var trigBtn = element.parent().find('button');
                    var trigIcn = trigBtn.find('i');
                    if (scope.open && event.target !== trigBtn[0] && event.target !== trigIcn[0]) {
                        scope.$apply(function() {
                            scope.open = false;
                        });
                    }
                };

                scope.$watch('open', function(value) {
                    if (value) {
                        $popupWrapper.offset(popupService.position(260, 270, element));
                        scope.$broadcast('datepicker.focus');
                        $document.bind('click', closeOnClick);
                    } else {
                        $document.unbind('click', closeOnClick);
                    }
                });

                var keydown = function(e) {
                    scope.keydown(e);
                };
                element.bind('keydown', keydown);

                scope.keydown = function(evt) {
                    if (evt.which === ESC) {
                        evt.preventDefault();
                        evt.stopPropagation();
                        scope.close();
                    } else {
                        if (evt.which === DOWN_ARROW && !scope.open) {
                            scope.open = true;
                        }
                    }
                };

                scope.close = function() {
                    scope.open = false;
                    element[0].focus();
                };

                var $popupWrapper = $compile(popup)(scope);
                popup.remove();
                $document.find('body').append($popupWrapper);

                scope.$on('$destroy', function() {
                    $popupWrapper.remove();
                    element.unbind('keydown', keydown);
                    $document.unbind('click', closeOnClick);
                });

            }
        };
    }

    function TimepickerDirective() {
        return {
            scope: {
                tt: '=ngModel',
                disabled: '=ngDisabled'
            },
            templateUrl: 'scripts/superdesk/ui/views/sd-timepicker.html',
            link: function(scope) {
            }
        };
    }

    TimepickerInnerDirective.$inject = ['$compile', '$document', 'popupService', 'datetimeHelper'];
    function TimepickerInnerDirective($compile, $document, popupService, datetimeHelper) {
        var popupTpl = '<div sd-timepicker-popup ' +
            'data-open="open" data-time="time" data-select="timeSelection({time: time})" data-keydown="keydown(e)">' +
            '</div>';
        return {
            scope: {
                open: '=opened'
            },
            require: 'ngModel',
            link: function(scope, element, attrs, ctrl) {

                var TIME_FORMAT = 'HH:mm:ss',
                    ESC = 27,
                    DOWN_ARROW = 40;
                var popup = angular.element(popupTpl);

                function viewFormat(time) {
                    //convert from utc time to local time
                    return moment(time, TIME_FORMAT).add(moment().utcOffset(), 'minutes').format(TIME_FORMAT);
                }

                ctrl.$parsers.unshift(function parseDate(viewValue) {
                    if (!viewValue) {
                        ctrl.$setValidity('time', true);
                        return null;
                    } else {
                        if (viewValue.tptime) {
                            ctrl.$setValidity('time', true);
                            return viewValue.tptime;
                        } else {
                            //value validation
                            if (datetimeHelper.isValidTime(viewValue)) {
                                ctrl.$setValidity('time', true);
                                scope.time = moment(viewValue, TIME_FORMAT).utc().format(TIME_FORMAT);
                                return scope.time;
                            } else {
                                //regex not passing
                                ctrl.$setValidity('time', false);
                                return null;
                            }
                        }
                    }
                });

                scope.timeSelection = function(tt) {
                    if (angular.isDefined(tt)) {
                        //if one of predefined time options is selected
                        scope.time = tt.time;
                        ctrl.$setViewValue({tptime: tt.time, viewtime: viewFormat(tt.time)});
                        ctrl.$render();
                    }
                    scope.close();
                };

                ctrl.$render = function() {
                    element.val(ctrl.$viewValue.viewtime);  //set the view
                    scope.time = ctrl.$viewValue.tptime;    //set timepicker model
                };

                //handle model changes
                ctrl.$formatters.unshift(function dateFormatter(modelValue) {
                    var tptime,
                        viewtime = 'Invalid Time';

                    if (modelValue) {
                        if (datetimeHelper.isValidTime(modelValue)) {
                            //formatter pass fine
                            tptime = modelValue;
                            viewtime =  viewFormat(modelValue);
                        }
                    } else {
                        viewtime = '';
                    }

                    return {
                        tptime: tptime,
                        viewtime: viewtime
                    };
                });

                scope.$watch('open', function(value) {
                    if (value) {
                        $popupWrapper.offset(popupService.position(200, 310, element));
                        scope.$broadcast('timepicker.focus');
                        $document.bind('click', closeOnClick);
                    } else {
                        $document.unbind('click', closeOnClick);
                    }
                });

                var closeOnClick = function(event) {
                    var trigBtn = element.parent().find('button');
                    var trigIcn = trigBtn.find('i');
                    if (scope.open && event.target !== trigBtn[0] && event.target !== trigIcn[0]) {
                        scope.$apply(function() {
                            scope.open = false;
                        });
                    }
                };

                var keydown = function(e) {
                    scope.keydown(e);
                };
                element.bind('keydown', keydown);

                scope.keydown = function(evt) {
                    if (evt.which === ESC) {
                        evt.preventDefault();
                        evt.stopPropagation();
                        scope.close();
                    } else {
                        if (evt.which === DOWN_ARROW && !scope.open) {
                            scope.open = true;
                        }
                    }
                };

                scope.close = function() {
                    scope.open = false;
                    element[0].focus();
                };

                var $popupWrapper = $compile(popup)(scope);
                popup.remove();
                $document.find('body').append($popupWrapper);

                scope.$on('$destroy', function() {
                    $popupWrapper.remove();
                });
            }
        };
    }

    TimepickerPopupDirective.$inject = ['$timeout'];
    function TimepickerPopupDirective($timeout) {
        return {
            templateUrl: 'scripts/superdesk/ui/views/sd-timepicker-popup.html',
            scope: {
                open: '=',
                select: '&',
                keydown: '&',
                time: '='
            },
            link: function(scope, element) {

                var TIME_FORMAT = 'HH:mm:ss';

                var POPUP = '.timepicker-popup';

                var focusElement = function() {
                    $timeout(function() {
                        element.find(POPUP).focus();
                    }, 0 , false);
                };

                scope.$on('timepicker.focus', focusElement);

                element.bind('click', function(event) {
                    event.preventDefault();
                    event.stopPropagation();
                });

                scope.hours = _.range(24);
                scope.minutes = _.range(0, 60, 5);

                scope.$watch('time', function(newVal, oldVal) {
                    var local;
                    if (newVal) {
                        //convert from utc to local
                        local = moment(newVal, TIME_FORMAT).add(moment().utcOffset(), 'minutes');
                    } else {
                        local = moment();
                    }
                    scope.hour = local.hour();
                    scope.minute = local.minute() - local.minute() % 5 + 5;
                    scope.second = local.second();
                });

                scope.submit = function(offset) {
                    var local, utc_time;
                    if (offset) {
                        local = moment().add(offset, 'minutes').format(TIME_FORMAT);
                    } else {
                        local = scope.hour + ':' + scope.minute + ':' + scope.second;
                    }
                    //convert from local to utc
                    utc_time = moment(local, TIME_FORMAT).utc().format(TIME_FORMAT);
                    scope.select({time: utc_time});
                };

                scope.cancel =  function() {
                    scope.select();
                };
            }
        };
    }

    /**
     * @memberof superdesk.ui
     * @ngdoc directive
     * @name sdTimepickerAlt
     * @description
     *   Timepicker directive saving utc time to model by defualt, and
     *   rendering local time.
     *
     *   Optionally, saving the UTC time to the model can be disabled by
     *   setting the no-utc-convert="true" attribute on the directive's DOM
     *   element. If this option is set, local time will be stored in the model
     *   (i.e. as picked by the user in the UI).
     *
     *   NOTE: the no-utc-convert attribute is only evaluated once, in the
     *   directive linking phase. Subsequent changes of the attribute value
     *   have no effect.
     */
    TimepickerAltDirective.$inject = ['tzdata'];
    function TimepickerAltDirective(tzdata) {
        var STEP = 5;

        function range(min, max, step) {
            step = step || 1;
            var items = [];
            for (var i = min; i <= max; i = i + step) {
                items.push(i);
            }
            return items;
        }

        return {
            scope: {
                model: '=',
                noUtcConvert: '@'
            },
            templateUrl: 'scripts/superdesk/ui/views/sd-timepicker-alt.html',
            link: function(scope) {

                var d = new Date(),
                    hours,
                    minutes,
                    utcConvert;

                utcConvert = (scope.noUtcConvert || '').toLowerCase() !== 'true';

                scope.open = false;
                scope.hoursRange = range(0, 23);
                scope.minutesRange = range(0, 59, STEP);

                tzdata.$promise.then(function () {
                    scope.timeZones = tzdata.getTzNames();
                });

                if (scope.model) {
                    hours = scope.model.substr(0, 2);
                    minutes = scope.model.substr(2, 2);

                    if (utcConvert) {
                        d.setUTCHours(hours);
                        d.setUTCMinutes(minutes);
                    } else {
                        d.setHours(hours);
                        d.setMinutes(minutes);
                    }
                } else {
                    d.setHours(0);
                    d.setMinutes(0);
                }

                // whether or not the model actually has a value
                scope.hasValue = !!scope.model;

                /**
                 * Set local hours
                 *
                 * @param {int} hours
                 */
                scope.setHours = function(hours) {
                    d.setHours(hours);
                    scope.hasValue = true;
                    update();
                };

                /**
                 * Set local minutes
                 *
                 * @param {int} minutes
                 */
                scope.setMinutes = function(minutes) {
                    d.setMinutes(minutes);
                    scope.hasValue = true;
                    update();
                };

                /**
                 * Toggle time picker on/off
                 */
                scope.toggle = function() {
                    scope.open = !scope.open;
                };

                /**
                 * Clears the model value (marking it as "no value selected").
                 *
                 * @method clearValue
                 */
                scope.clearValue = function () {
                    d.setHours(0);
                    d.setMinutes(0);
                    scope.hasValue = false;
                    update();
                };

                update();

                /**
                 * Update scope using local time and model using utc time
                 */
                function update() {
                    if (scope.hasValue) {
                        scope.hours = d.getHours();
                        scope.minutes = d.getMinutes();
                        scope.model = utcConvert ? utc() : noUtcTime(d);
                    } else {
                        scope.hours = 0;
                        scope.minutes = 0;
                        scope.model = '';
                    }
                }

                /**
                 * Get utc time for model
                 *
                 * @return {string} utc time in format `HHMM`
                 */
                function utc() {
                    var hours = d.getUTCHours().toString();
                    var minutes = d.getUTCMinutes().toString();
                    return ('00' + hours).slice(-2) + ('00' + minutes).slice(-2);
                }

                /**
                 * Returns the '%H%M' time string (i.e. double-digit hour and
                 * minute parts) from the given Date object using local time.
                 *
                 * @function noUtcTime
                 * @param {Date} d
                 * @return {string}
                 */
                function noUtcTime(d) {
                    var hours = ('00' + d.getHours()).slice(-2),
                        minutes = ('00' + d.getMinutes()).slice(-2);
                    return hours + minutes;
                }
            }
        };
    }

    function LeadingZeroFilter() {
        return function(input) {
            if (input < 10) {
                input = '0' + input;
            }
            return input;
        };
    }

    DateTimeHelperService.$inject = [];
    function DateTimeHelperService() {

        this.isValidTime = function(value) {
            //checking if the given value is a time in a format 'hh:mm:ss'
            var colonCount = 0;
            var hh, mm, ss;

            for (var i = 0; i < value.length; i++) {
                var ch = value.substring(i, i + 1);
                if (((ch < '0') || (ch > '9')) && (ch !== ':')) {
                    return false;
                }
                if (ch === ':') { colonCount++; }
            }

            if (colonCount !== 2) {return false;}

            hh = value.substring(0, value.indexOf(':'));
            if (hh.length !== 2 || (parseFloat(hh) < 0) || (parseFloat(hh) > 23)) {return false;}

            mm = value.substring(value.indexOf(':') + 1, value.lastIndexOf(':'));
            if (mm.length !== 2 || (parseFloat(mm) < 0) || (parseFloat(mm) > 59)) {return false;}

            ss = value.substring(value.lastIndexOf(':') + 1, value.length);
            if (ss.length !== 2 || (parseFloat(ss) < 0) || (parseFloat(ss) > 59)) {return false;}

            return true;
        };

        this.isValidDate = function(value) {
            //checking if the given value is a date in a format '31/01/2000'
            var pattern = /^(0?[1-9]|[12][0-9]|3[01])\/(0?[1-9]|1[012])\/(19\d{2}|[2-9]\d{3})$/;
            var regex = new RegExp(pattern);
            return regex.test(value);
        };

        this.mergeDateTime = function(date, time) {
            var date_str = moment(date).format('YYYY-MM-DD');
            var time_str = moment(time, 'HH:mm:ss').add(moment().utcOffset(), 'minute').format('HH:mm:ss');
            var merge_str = date_str + ' ' + time_str;
            return moment(merge_str, 'YYYY-MM-DD HH:mm:ss').utc();
        };
    }

    WeekdayPickerDirective.$inject = ['weekdays'];
    function WeekdayPickerDirective(weekdays) {
        return {
            templateUrl: 'scripts/superdesk/ui/views/weekday-picker.html',
            scope: {model: '='},
            link: function(scope) {
                scope.weekdays = weekdays;
                scope.weekdayList = Object.keys(weekdays);

                scope.model = scope.model || [];

                /**
                 * Test if given day is selected for schedule
                 *
                 * @param {string} day
                 * @return {boolean}
                 */
                scope.isDayChecked = function(day) {
                    return scope.model.indexOf(day) !== -1;
                };

                /**
                 * Toggle given day on/off
                 *
                 * @param {string} day
                 */
                scope.toggleDay = function(day) {
                    if (scope.isDayChecked(day)) {
                        scope.model.splice(scope.model.indexOf(day), 1);
                    } else {
                        scope.model.push(day);
                    }
                };
            }
        };
    }

    return angular.module('superdesk.ui', ['superdesk.dashboard.world-clock'])

        .directive('sdShadow', ShadowDirective)
        .directive('sdAutoHeight', require('./autoheight-directive'))
        .directive('sdToggleBox', ToggleBoxDirective)
        .filter('nl2el', NewlineToElement)
        .factory('WizardHandler', WizardHandlerFactory)
        .directive('sdWizard', WizardDirective)
        .directive('sdWizardStep', WizardStepDirective)
        .directive('sdCreateBtn', CreateButtonDirective)
        .directive('sdAutofocus', AutofocusDirective)
        .directive('sdAutoexpand', AutoexpandDirective)
        .directive('sdDatepickerInner', DatepickerInnerDirective)
        .directive('sdDatepickerWrapper', DatepickerWrapper)
        .directive('sdDatepicker', DatepickerDirective)
        .directive('sdTimepickerInner', TimepickerInnerDirective)
        .directive('sdTimepickerPopup', TimepickerPopupDirective)
        .directive('sdTimepicker', TimepickerDirective)
        .directive('sdTimepickerAlt', TimepickerAltDirective)
        .service('popupService', PopupService)
        .service('datetimeHelper', DateTimeHelperService)
        .filter('leadingZero', LeadingZeroFilter)
        .directive('sdDropdownPosition', DropdownPositionDirective)
        .directive('sdDropdownPositionRight', DropdownPositionRightDirective)
        .directive('sdWeekdayPicker', WeekdayPickerDirective)
        ;
});
