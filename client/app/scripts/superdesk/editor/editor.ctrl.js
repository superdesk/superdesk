(function() {
'use strict';

angular.module('superdesk.editor').controller('SdTextEditorController', SdTextEditorController);

SdTextEditorController.$inject = ['lodash', 'EMBED_PROVIDERS', 'dragulaService', '$scope', '$timeout'];
function SdTextEditorController(_, EMBED_PROVIDERS, dragulaService, $scope, $timeout) {
    var vm = this;
    function Block(attrs) {
        angular.extend(this, {
            body: attrs && attrs.body || '',
            caption: attrs && attrs.caption || undefined,
            blockType: attrs && attrs.blockType || 'text',
            embedType: attrs && attrs.embedType || undefined,
            lowerAddEmbedIsExtented: undefined,
            showAndFocusLowerAddAnEmbedBox: function() {
                this.lowerAddEmbedIsExtented = true;
            },
        });
    }
    /**
    * For the given blocks, merge text blocks when there are following each other and add empty text block arround embeds if needed
    */
    function prepareBlocks(blocks) {
        var newBlocks = [];
        blocks.forEach(function(block, i) {
            // if not the first block and there is a text block following another one
            if (i > 0 && block.blockType === 'text' && blocks[i - 1].blockType === 'text') {
                // we merge the content with the previous block
                newBlocks[newBlocks.length - 1].body += block.body;
            } else {
                // otherwise we add the full block
                newBlocks.push(block);
            }
            // add emtpy text block if block is between 2 embed blocks or at the end
            if (blocks[i].blockType === 'embed') {
                if (i === blocks.length - 1 || blocks[i + 1].blockType === 'embed') {
                    newBlocks.push(new Block());
                }
            }
        });
        // add emtpy text block at the top if needed
        if (newBlocks[0].blockType === 'embed') {
            newBlocks.unshift(new Block());
        }
        return newBlocks;
    }
    angular.extend(vm, {
        blocks: [],
        initEditorWithOneBlock: function(model) {
            vm.model = model;
            vm.blocks = [new Block({body: model.$modelValue})];
        },
        initEditorWithMultipleBlock: function(model) {
            var blocks = [], block;
            /**
             * push the current block into the blocks collection if it is not empty
             */
            function commitBlock() {
                if (block !== undefined && block.body.trim() !== '') {
                    blocks.push(block);
                    block = undefined;
                }
            }
            // save the model to update it later
            vm.model = model;
            // parse the given model and create blocks per paragraph and embed
            var content = model.$modelValue || '';
            $('<div>' + content + '</div>')
            .contents()
            .toArray()
            .forEach(function(element) {
                // if we get a <p>, we push the current block and create a new one
                // for the paragraph content
                if (element.nodeName === 'P') {
                    commitBlock();
                    if (angular.isDefined(element.innerHTML) && element.textContent !== '' && element.textContent !== '\n') {
                        blocks.push(new Block({body: element.outerHTML.trim()}));
                    }
                // detect if it's an embed
                } else if (element.nodeName === '#comment') {
                    if (element.nodeValue.indexOf('EMBED START') > -1) {
                        commitBlock();
                        // retrieve the embed type following the comment
                        var embed_type = angular.copy(element.nodeValue).replace(' EMBED START ', '').trim();
                        if (embed_type === '') {
                            embed_type = EMBED_PROVIDERS.custom;
                        }
                        // create the embed block
                        block = new Block({blockType: 'embed', embedType: embed_type});
                    }
                    if (element.nodeValue.indexOf('EMBED END') > -1) {
                        commitBlock();
                    }
                // if it's not a paragraph or an embed, we update the current block
                } else {
                    if (block === undefined) {
                        block = new Block();
                    }
                    // we want the outerHTML (ex: '<b>text</b>') or the node value for text and comment
                    block.body += (element.outerHTML || element.nodeValue || '').trim();
                }
            });
            // at the end of the loop, we push the last current block
            if (block !== undefined && block.body.trim() !== '') {
                blocks.push(block);
            }
            // extract body and caption from embed block
            blocks.forEach(function(block) {
                if (block.blockType === 'embed') {
                    var original_body = angular.element(angular.copy(block.body));
                    if (original_body.get(0).nodeName === 'FIGURE') {
                        block.body = '';
                        original_body.contents().toArray().forEach(function(element) {
                            if (element.nodeName === 'FIGCAPTION') {
                                block.caption = element.innerHTML;
                            } else {
                                block.body += element.outerHTML || element.nodeValue || '';
                            }
                        });
                    }
                }
            });
            // if no block, create an empty one to start
            if (blocks.length === 0) {
                blocks.push(new Block());
            }
            // update the actual blocks value at the end to prevent more digest cycle as needed
            vm.blocks = blocks;
            vm.renderBlocks();
        },
        commitChanges: function() {
            var new_body = '';
            if (vm.config.multiBlockEdition) {
                vm.blocks.forEach(function(block) {
                    if (angular.isDefined(block.body) && block.body.trim() !== '') {
                        if (block.blockType === 'embed') {
                            new_body += [
                                '<!-- EMBED START ' + block.embedType.trim() + ' -->\n',
                                '<figure>',
                                block.body,
                                '<figcaption>',
                                block.caption,
                                '</figcaption>',
                                '</figure>',
                                '\n<!-- EMBED END ' + block.embedType.trim() + ' -->\n'].join('');
                        } else {
                            new_body += block.body + '\n';
                        }
                    }
                });
            } else {
                if (vm.blocks[0].body.trim() === '<br>') {
                    vm.blocks[0].body = '';
                }
                new_body = vm.blocks[0].body;
            }
            vm.model.$setViewValue(new_body);
        },
        getBlockPosition: function(block) {
            return _.indexOf(vm.blocks, block);
        },
        /**
        ** Merge text blocks when there are following each other and add empty text block arround embeds if needed
        ** @param {Integer} position
        ** @param {Object} block ; block attributes
        ** @param {boolean} unprocess ; if true, it won't merge text blocks and
        ** add empty text block if needed through the `renderBlocks()` function.
        ** @returns {object} this
        */
        insertNewBlock: function(position, attrs, unprocess) {
            var new_block = new Block(attrs);
            vm.blocks.splice(position, 0, new_block);
            if (!unprocess) {
                vm.renderBlocks();
            }
            $timeout(vm.commitChanges);
            return this;
        },
        /**
        * Merge text blocks when there are following each other and add empty text block arround embeds if needed
        */
        renderBlocks: function() {
            vm.blocks = prepareBlocks(vm.blocks);
        },
        removeBlock: function(block) {
            // remove block only if it's not the only one
            var block_position = vm.getBlockPosition(block);
            if (vm.blocks.length > 1) {
                vm.blocks.splice(block_position, 1);
            } else {
                // if it's the first block, just remove the content
                block.body = '';
            }
            vm.renderBlocks();
            $timeout(vm.commitChanges);
        },
        getPreviousBlock: function(block) {
            var pos = vm.getBlockPosition(block);
            // if not the first one
            if (pos > 0) {
                return vm.blocks[pos - 1];
            }
        }
    });
    var dragulaBagName = 'blocks';
    dragulaService.options($scope, dragulaBagName, {
        revertOnSpill: true,
        moves: function (el, container, handle) {
            return handle.className === 'block__move';
        }
    });
    $scope.$on(dragulaBagName + '.drop-model', function (el, target, source) {
        // vm.renderBlocks();
        vm.commitChanges();
    });
}
})();
