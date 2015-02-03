define(['angular'], function(angular) {
    'use strict';

    return function() {

        var URL = window.URL || window.webkitURL;

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
    };
});
