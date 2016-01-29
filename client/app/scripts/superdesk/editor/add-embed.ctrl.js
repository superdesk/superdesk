(function() {
'use strict';

angular.module('superdesk.editor').controller('SdAddEmbedController', SdAddEmbedController);

SdAddEmbedController.$inject = ['embedService', '$element', '$timeout', '$q', 'lodash', 'EMBED_PROVIDERS', '$scope'];
function SdAddEmbedController (embedService, $element, $timeout, $q, _, EMBED_PROVIDERS, $scope) {
    var vm = this;
    angular.extend(vm, {
        editorCtrl: undefined,  // defined in link method
        previewLoading: false,
        // extended: angular.isDefined(vm.extended) ? vm.extended : undefined,
        toggle: function(close) {
            // use parameter or toggle
            vm.extended = angular.isDefined(close) ? !close : !vm.extended;
        },
        /**
         * Return html code to represent an embedded picture
         *
         * @param {string} url
         * @param {string} description
         * @return {string} html
         */
        pictureToHtml: function(url, description) {
            var html = '<img alt="' + (description || '') + '" src="' + url + '">\n';
            return html;
        },
        /**
         * Return html code to represent an embedded link
         *
         * @param {string} url
         * @param {string} title
         * @param {string} description
         * @param {string} illustration
         * @return {string} html
         */
        linkToHtml: function(url, title, description, illustration) {
            var html = [
                '<div class="embed--link">',
                angular.isDefined(illustration) ?
                '  <img src="' + illustration + '" class="embed--link__illustration"/>' : '',
                '  <div class="embed--link__title">',
                '      <a href="' + url + '" target="_blank">' + title + '</a>',
                '  </div>',
                '  <div class="embed--link__description">' + description + '</div>',
                '</div>'];
            return html.join('\n');
        },
        retrieveEmbed:function() {
            // if it's an url, use embedService to retrieve the embed code
            var embedCode;
            if (_.startsWith(vm.input, 'http')) {
                embedCode = embedService.get(vm.input).then(function(data) {
                    var embed = data.html;
                    if (!angular.isDefined(embed)) {
                        if (data.type === 'photo') {
                            embed = vm.pictureToHtml(data.url, data.description);
                        } else if (data.type === 'link') {
                            embed = vm.linkToHtml(data.url, data.title, data.description, data.thumbnail_url);
                        }
                    }
                    return {
                        body: embed,
                        provider: data.provider_name || EMBED_PROVIDERS.custom
                    };
                });
            // otherwise we use the content of the field directly
            } else {
                var embedType = EMBED_PROVIDERS.custom;
                // try to guess the provider of the custom embed
                if (vm.input.indexOf('twitter.com/widgets.js') > -1) {
                    embedType = EMBED_PROVIDERS.twitter;
                } else if (vm.input.indexOf('https://www.youtube.com') > -1){
                    embedType = EMBED_PROVIDERS.youtube;
                }
                embedCode = $q.when({
                    body: vm.input,
                    provider: embedType
                });
            }
            return embedCode;
        },
        updatePreview: function() {
            vm.previewLoading = true;
            vm.retrieveEmbed().then(function(embed) {
                angular.element($element).find('.preview').html(embed.body);
                vm.previewLoading = false;
            });
        },
        createFigureBlock: function(embedType, body, caption) {
            // create a new block containing the embed
            return vm.editorCtrl.insertNewBlock(vm.addToPosition, {
                blockType: 'embed',
                embedType: embedType,
                body: body,
                caption: caption
            });
        },
        createBlockFromEmbed: function() {
            vm.retrieveEmbed().then(function(embed) {
                vm.createFigureBlock(embed.provider, embed.body);
                // close the addEmbed form
                vm.toggle(true);
            });
        },
        createBlockFromSdPicture: function(img, item) {
            var html = vm.pictureToHtml(img.href, item.description);
            vm.createFigureBlock('Image', html, item.description);
        }
    });

    // toggle when the `extended` directive attribute changes
    $scope.$watch(function() {
        return vm.extended;
    }, function(extended) {
        // on enter, focus on input
        if (angular.isDefined(extended)) {
            if (extended) {
                $timeout(function() {
                    angular.element($element).find('input').focus();
                });
                // on leave, clear field
            } else {
                vm.input = '';
                vm.onClose();
            }
        }
    });
}
})();
