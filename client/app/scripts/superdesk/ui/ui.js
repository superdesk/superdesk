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

                this.addStep = function(step) {
                    $scope.steps.push(step);
                };

                $scope.$watch('currentStep', function(stepCode) {
                    if (stepCode && (($scope.selectedStep && $scope.selectedStep.code !== stepCode) || !$scope.selectedStep)) {
                        $scope.goTo(_.findWhere($scope.steps, {code: stepCode}));
                    }
                });

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
                code: '@'
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
                _.defer(function() {
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
                dt: '=ngModel'
            },
            templateUrl: 'scripts/superdesk/ui/views/sd-datepicker.html'
        };
    }

    DatepickerInnerDirective.$inject = ['$compile', '$document'];
    function DatepickerInnerDirective($compile, $document) {
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

                var VIEW_FORMAT = 'DD/MM/YYYY';
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
                            //value validation
                            var pattern = /^(0?[1-9]|[12][0-9]|3[01])\/(0?[1-9]|1[012])\/(19\d{2}|[2-9]\d{3})$/;
                            var regex = new RegExp(pattern);

                            if (regex.test(viewValue)) {
                                if (moment(viewValue, VIEW_FORMAT).isValid()) {
                                    ctrl.$setValidity('date', true);
                                    return moment(viewValue, VIEW_FORMAT).utc().format();
                                } else {
                                    //value cannot be converted
                                    ctrl.$setValidity('date', false);
                                    return null;
                                }
                            } else {
                                //regex not passing
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
                    scope.open = false;
                    element[0].focus();
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
                        setPosition();
                        scope.$broadcast('datepicker.focus');
                        $document.bind('click', closeOnClick);
                    } else {
                        $document.unbind('click', closeOnClick);
                    }
                });

                function setPosition() {
                    //taking care of screen size and responsiveness
                    var tolerance = 10;
                    var dpHeight = 270, dpWidth = 260;
                    var elOffset = element.offset();
                    var elHeight = element.outerHeight();
                    var docHeight = $document.height();
                    var docWidth = $document.width();

                    var position = {top: 0, left:0};

                    if ((elOffset.top + elHeight + dpHeight + tolerance) > docHeight) {
                        position.top = elOffset.top - dpHeight;
                    } else {
                        position.top = elOffset.top + elHeight;
                    }

                    if ((elOffset.left + dpWidth + tolerance) > docWidth) {
                        position.left = docWidth - tolerance - dpWidth;
                    } else {
                        position.left = elOffset.left;
                    }
                    $popupWrapper.offset(position);
                }

                var keydown = function(e) {
                    scope.keydown(e);
                };
                element.bind('keydown', keydown);

                scope.keydown = function(evt) {
                    if (evt.which === 27) {
                        evt.preventDefault();
                        evt.stopPropagation();
                        scope.close();
                    } else {
                        if (evt.which === 40 && !scope.open) {
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

    return angular.module('superdesk.ui', [])

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
        .directive('sdDatepicker', DatepickerDirective);
});
