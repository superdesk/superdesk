define([
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
     * <div sd-image-crop
     *  data-src="data.renditions.viewImage.href"
     *  data-show-Min-Size-Error="true"
     *  data-crop-init="preview.cords"
     *  data-box-width="800"
     *  data-box-height="600"
     *  data-min-size="[800, 600]"
     *  data-crop-select="[0, 0, 800, 600]">
     * </div>
     *
     * @data-cords attribute used to provide updated crop coordinates in preview.cords
     * scope.preview should be define on container page so that the coordiates can be used
     * to pass in api that is serving for saving the crop.
     */
    return ['gettext', '$interpolate', 'imageFactory', function(gettext, $interpolate, imageFactory) {
        return {
            scope: {
                src: '=',
                cropInit: '=',
                cropData: '=',
                onChange: '&',
                original: '=',
                rendition: '=',
                boxWidth: '=',
                boxHeight: '=',
                showMinSizeError: '='
            },
            link: function(scope, elem) {

                /**
                 * Updates crop coordinates scope
                 *
                 * @param {Array} cords
                 */
                function updateScope(cords) {
                    var nextData = formatCoordinates(cords);
                    var prevData = scope.cropData || scope.cropInit;
                    if (!angular.equals(nextData, prevData)) {
                        scope.$apply(function() {
                            scope.cropData = nextData;
                            scope.onChange({cropData: nextData});
                        });
                    }
                }

                /**
                 * Format jCrop coordinates into superdesk crop specs
                 *
                 * @param {Object} cords jCrop coordinates
                 * @return {Object} superdesk crop specs
                 */
                function formatCoordinates(cords) {
                    return {
                        CropLeft: Math.round(Math.min(cords.x, cords.x2)),
                        CropRight: Math.round(Math.max(cords.x, cords.x2)),
                        CropTop: Math.round(Math.min(cords.y, cords.y2)),
                        CropBottom: Math.round(Math.max(cords.y, cords.y2))
                    };
                }

                /**
                 * Parse superdesk crop specs into jCrop coordinates
                 *
                 * @param {Object} cropImage
                 * @return {Array} [x0, y0, x1, y1]
                 */
                function parseCoordinates(cropImage) {
                    if (cropImage != null && cropImage.CropLeft != null) {
                        return [
                            cropImage.CropLeft,
                            cropImage.CropTop,
                            cropImage.CropRight,
                            cropImage.CropBottom
                        ];
                    }
                }

                scope.$watch('src', function(src) {
                    elem.empty();
                    if (!src) {
                        return;
                    }

                    var img = imageFactory.makeInstance();
                    img.onload = function() {
                        var cropSelect = parseCoordinates(scope.cropInit) || getDefaultCoordinates(scope.original, scope.rendition);

                        if (scope.showMinSizeError && !validateConstraints(scope.original, scope.rendition)) {
                            return;
                        }

                        elem.append(img);
                        $(img).Jcrop({
                            aspectRatio: scope.rendition.width / scope.rendition.height,
                            minSize: [scope.rendition.width, scope.rendition.height],
                            trueSize: [scope.original.width, scope.original.height],
                            boxWidth: scope.boxWidth,
                            boxHeight: scope.boxHeight,
                            setSelect: cropSelect,
                            allowSelect: false,
                            addClass: 'jcrop-dark',
                            onSelect: updateScope
                        });
                    };

                    img.src = src;
                });

                function validateConstraints(img, rendition) {
                    if (img.width < rendition.width || img.height < rendition.height) {
                        scope.$apply(function() {
                            var text = $interpolate(
                                gettext('Sorry, but image must be at least {{ r.width }}x{{ r.height }},' +
                                        ' (it is {{ img.width }}x{{ img.height }}).')
                            )({
                                r: rendition,
                                img: img
                            });

                            elem.append('<p class="error">' + text);
                        });

                        return false;
                    }

                    return true;
                }

                /**
                 * Get the largest part of image matching required specs.
                 *
                 * @param {Object} img
                 * @param {Object} rendition
                 * @return {Array} [x0, y0, x1, y1]
                 */
                function getDefaultCoordinates(img, rendition) {
                    var ratio = Math.min(img.width / rendition.width, img.height / rendition.height);
                    var width = Math.floor(ratio * rendition.width);
                    var height = Math.floor(ratio * rendition.height);
                    var x0 = Math.floor((img.width - width) / 2);
                    var y0 = Math.floor((img.height - height) / 2);
                    return [x0, y0, x0 + width, y0 + height];
                }
            }
        };
    }];
});
