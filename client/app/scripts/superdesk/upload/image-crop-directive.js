define([
    'lodash',
    'bower_components/jcrop/js/jquery.Jcrop'
], function(_) {
    'use strict';

    return ['notify', 'gettext', function(notify, gettext) {
        return {
            scope: {
                src: '=',
                cords: '=',
                progressWidth: '=',
                boxWidth: '=',
                boxHeight: '=',
                aspectRatio: '=',
                minimumSize: '=',
                showMinSizeError: '='
            },
            link: function(scope, elem) {

                var bounds, boundx, boundy;
                var rwidth, rheight;
                var jcrop_api;
                var minimumSize;

                minimumSize = scope.minimumSize ? scope.minimumSize : [200, 200];

                console.log('eval=' + scope.aspectRatio);
                console.log('minSize=' + scope.minimumSize);

                // To adjust preview box as per aspect ratio
                if (scope.aspectRatio.toFixed(2) === '1.33') {
                    rwidth = 300; rheight = 225;
                } else if (scope.aspectRatio.toFixed(2) === '1.78') {
                    rwidth = 300; rheight = 169;
                } else {
                    rwidth = 300; rheight = 300;
                }

                var updateScope = _.throttle(function(c) {
                    scope.$apply(function() {
                        scope.cords = c;
                        var rx = rwidth / scope.cords.w;
                        var ry = rheight / scope.cords.h;
                        showPreview('.preview-target-1', rx, ry, boundx, boundy, scope.cords.x, scope.cords.y);
                        //showPreview('.preview-target-2', rx / 2, ry / 2, boundx, boundy, scope.cords.x, scope.cords.y);
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

                function validateConstraints(imgObj) {
                    if (imgObj.width < minimumSize[0] || imgObj.height < minimumSize[1]) {
                        scope.$apply(function() {
                            notify.pop();
                            notify.error(gettext('Sorry, but image must be at least ' + minimumSize[0] + 'x' + minimumSize[1]));
                            scope.src = null;
                            scope.progressWidth = 0;
                            scope.$parent.preview.progress = null;
                        });
                        return;
                    }
                }

                scope.$watch('src', function(src) {
                    elem.empty();
                    if (src) {
                        var img = new Image();
                        img.onload = function() {
                            scope.progressWidth = 80;
                            scope.$parent.preview.progress = true;
                            var size = [this.width, this.height];
                            /*console.log('size=' + size);
                            console.log('scope.boxWidth=' + scope.boxWidth);*/

                            if (scope.showMinSizeError) {
                                validateConstraints(this);
                            }

                            elem.append(img);
                            $(img).Jcrop({
                                aspectRatio: scope.aspectRatio,
                                minSize: minimumSize,
                                trueSize: size,
                                boxWidth: scope.boxWidth,
                                boxHeight: scope.boxHeight,
                                //setSelect: [0, 0, Math.min.apply(size), Math.min.apply(size)],
                                setSelect: [0, 0, scope.boxWidth, scope.boxHeight],
                                allowSelect: false,
                                bgColor: 'white',
                                bgOpacity: 0.9,
                                onChange: updateScope
                            }, function() {
                                jcrop_api = this;
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
    }];
});
