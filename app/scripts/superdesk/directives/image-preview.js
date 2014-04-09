define(['angular', 'lodash', 'bower_components/jcrop/js/jquery.Jcrop'], function(angular, _) {
    'use strict';

    var URL = window.URL || window.webkitURL;

    var module = angular.module('superdesk');

    module.directive('sdImagePreview', ['notify', 'gettext', function(notify, gettext) {
        var IS_IMG_REGEXP = /^image\//;
        return {
            scope: {
                file: '=',
                sdImagePreview: '=',
                progressWidth: '='
            },
            link: function(scope, elem) {

                function updatePreview(e) {
                    scope.$apply(function() {
                        scope.sdImagePreview = e.target.result;
                        scope.progressWidth = 50;
                    });
                }

                scope.$watch('file', function(file) {
                    if (file && IS_IMG_REGEXP.test(file.type)) {
                        scope.progressWidth = 30; // will continue in sd-crop
                        var fileReader = new FileReader();
                        fileReader.onload = updatePreview;
                        fileReader.readAsDataURL(file);
                    } else if (file) {
                        notify.pop();
                        notify.error(gettext('Sorry, but given file type is not supported.'));
                    }
                });
            }
        };
    }]);

    module.directive('sdVideoCapture', function() {

        var DATA_URL_REGEXP = /^data:([a-z\/]+);(base64,)?(.*)$/;

        navigator.getMedia = (navigator.getUserMedia ||
            navigator.webkitGetUserMedia ||
            navigator.mozGetUserMedia ||
            navigator.msGetUserMedia);

        return {
            scope: {
                sdVideoCapture: '=',
                file: '='
            },
            link: function(scope, elem) {
                var localMediaStream = null,
                    canvas = angular.element('<canvas style="display:none"></canvas>'),
                    ctx = canvas[0].getContext('2d'),
                    tooLate = false;

                elem.after(canvas);

                navigator.getMedia({
                    video: true,
                    audio: false
                }, function(stream) {
                    if (tooLate) {
                        stream.stop();
                        return;
                    }

                    localMediaStream = stream;
                    if (navigator.mozGetUserMedia) {
                        elem[0].mozSrcObject = stream;
                    } else {
                        elem[0].src = URL.createObjectURL(stream);
                    }
                }, function(err) {
                    console.error('There was an error when getting media: ' + err);
                });

                elem.click(function(e) {
                    var img = elem[0];
                    canvas[0].width = img.videoWidth;
                    canvas[0].height = img.videoHeight;
                    ctx.drawImage(img, 0, 0);

                    // todo(petr): use canvas.toBlog once available in chrome
                    scope.$apply(function() {
                        scope.sdVideoCapture = canvas[0].toDataURL('image/jpeg', 0.95);
                        var matches = DATA_URL_REGEXP.exec(scope.sdVideoCapture);
                        if (matches.length === 4) {
                            scope.file = new Blob([atob(matches[3])], {type: matches[1]});
                        }
                    });
                });

                scope.$on('$destroy', function() {
                    try {
                        tooLate = true;
                        elem[0].pause();
                        localMediaStream.stop();
                    } catch (err) {}
                });
            }
        };
    });

    module.directive('sdCrop', ['notify', 'gettext', function(notify, gettext) {
        return {
            scope: {
                src: '=',
                cords: '=',
                progressWidth: '='
            },
            link: function(scope, elem) {

                var bounds, boundx, boundy;

                var updateScope = _.throttle(function(c) {
                    scope.$apply(function() {
                        scope.cords = c;
                        var rx = 120 / scope.cords.w;
                        var ry = 120 / scope.cords.h;
                        showPreview('.preview-target-1', rx, ry, boundx, boundy, scope.cords.x, scope.cords.y);
                        showPreview('.preview-target-2', rx / 2, ry / 2, boundx, boundy, scope.cords.x, scope.cords.y);
                    });
                }, 300);

                function showPreview(e, rx, ry, boundx, boundy, cordx, cordy) {
                    $(e).css({
                        width: Math.round(rx * boundx) + 'px',
                        height: Math.round(ry * boundy) + 'px',
                        marginLeft: '-' + Math.round(rx * cordx) + 'px',
                        marginTop: '-' + Math.round(ry * cordy) + 'px'
                    });
                }

                scope.$watch('src', function(src) {
                    elem.empty();
                    if (src) {
                        console.time('img');
                        var img = new Image();
                        img.onload = function() {
                            scope.progressWidth = 80;
                            var size = [this.width, this.height];

                            if (this.width < 200 || this.height < 200) {
                                scope.$apply(function() {
                                    notify.pop();
                                    notify.error(gettext('Sorry, but avatar must be at least 200x200 pixels big.'));
                                    scope.src = null;
                                    scope.progressWidth = 0;
                                });

                                return;
                            }

                            elem.append(img);
                            $(this).Jcrop({
                                aspectRatio: 1.0,
                                minSize: [200, 200],
                                trueSize: size,
                                boxWidth: 300,
                                boxHeight: 225,
                                setSelect: [0, 0, Math.min.apply(size), Math.min.apply(size)],
                                allowSelect: false,
                                onChange: updateScope
                            }, function() {
                                bounds = this.getBounds();
                                boundx = bounds[0];
                                boundy = bounds[1];
                            });
                            scope.progressWidth = 0;
                        };
                        img.src = src;
                    }
                });
            }
        };
    }]);
});
