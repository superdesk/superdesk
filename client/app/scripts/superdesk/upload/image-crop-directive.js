define([
    'lodash',
    'bower_components/jcrop/js/jquery.Jcrop'
], function(_) {
    'use strict';
    /**
     * sd-image-crop based on Jcrop tool and provides Image crop functionality for
     * provided Aspect ratio and other attributes.
     * For Complete Usage of Jcrop:
     * refer to http://deepliquid.com/content/Jcrop_Manual.html
     *
     * Example Usage:
     * <div sd-image-crop data-src="data.renditions.original.href" data-show-Min-Size-Error="true"
     *  data-cords="preview.cords" data-box-width="800" data-box-height="600"
     *  data-aspect-ratio="4/3" data-minimum-size="[800, 600]"
     *  data-crop-select="[0, 0, 800, 600]">
     * </div>
     *
     * @data-cords attribute used to provide updated crop coordinates in preview.cords
     * scope.preview should be define on container page so that the coordiates can be used
     * to pass in api that is serving for saving the crop.
     */
    return ['notify', 'gettext', '$timeout', 'imageFactory', function(notify, gettext, $timeout, imageFactory) {
        return {
            scope: {
                src: '=',
                cords: '=',
                boxWidth: '=',
                boxHeight: '=',
                aspectRatio: '=',
                minimumSize: '=',
                cropSelect: '=',
                showMinSizeError: '='
            },
            link: function(scope, elem) {

                var bounds, boundx, boundy;
                var rwidth, rheight;
                var minimumSize, updateTimeout;
                var cropSelect = [];

                minimumSize = scope.minimumSize ? scope.minimumSize : [200, 200];
                cropSelect = scope.cropSelect ? getCropSelect(scope.cropSelect) : [0, 0, scope.boxWidth, scope.boxHeight];

                /**
                * Push value in clockwise sequence from Left, Top, Right then Bottom (L-T-R-B).
                */
                function getCropSelect(cropImage) {
                    cropSelect.length = 0;

                    cropSelect.push(cropImage.CropLeft);
                    cropSelect.push(cropImage.CropTop);
                    cropSelect.push(cropImage.CropRight);
                    cropSelect.push(cropImage.CropBottom);

                    return cropSelect;
                }

                // To adjust preview box as per aspect ratio.
                if (scope.aspectRatio) {
                    if (scope.aspectRatio.toFixed(2) === '1.33') {  // 4/3 ratio
                        rwidth = 300; rheight = 225;
                    } else if (scope.aspectRatio.toFixed(2) === '1.78') {   // 16/9 ratio
                        rwidth = 300; rheight = 169;
                    } else {
                        rwidth = 300; rheight = 300;
                    }
                } else {
                    notify.error(gettext('sdImageCrop: attribute "aspect-ratio" is mandatory'));
                    throw new Error('sdImageCrop: attribute "aspect-ratio" is mandatory');
                }

                /**
                 * Invoked on Jcrops' onChange event to call updateScope(c) with coordinates
                */
                var updateFunc = function(c) {
                    cancelTimeout(c);
                    updateTimeout = $timeout(updateScope(c), 300, false);
                };

                function cancelTimeout(event) {
                    $timeout.cancel(updateTimeout);
                }

                /**
                 * Updates crop coordinates scope and invokes showPreview function for crop preview.
                */
                function updateScope(c) {
                    scope.$apply(function() {
                        scope.cords = c;
                        var rx = rwidth / scope.cords.w;
                        var ry = rheight / scope.cords.h;
                        showPreview('.preview-target-1', rx, ry, boundx, boundy, scope.cords.x, scope.cords.y);
                    });
                }

                /**
                 * Applies the css to display selected crop in preview box,
                 * respective to the selected aspect ratio
                 */
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
                            scope.$parent.preview.progress = null;
                            throw new Error('sdImageCrop: Sorry, but image must be at least ' + minimumSize[0] + 'x' + minimumSize[1]);
                        });
                    }
                }

                scope.$watch('src', function(src) {
                    elem.empty();
                    if (!src) {
                        return;
                    }
                    var img = imageFactory.makeInstance();
                    img.onload = function() {
                        scope.$parent.preview.progress = true;
                        var size = [this.width, this.height];
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
                            setSelect: cropSelect,
                            allowSelect: false,
                            addClass: 'jcrop-dark',
                            onChange: updateFunc
                        }, function() {
                            bounds = this.getBounds();
                            boundx = bounds[0];
                            boundy = bounds[1];
                            updateFunc(scope.cords);
                        });
                    };
                    img.src = src;
                });
            }
        };
    }];
});
