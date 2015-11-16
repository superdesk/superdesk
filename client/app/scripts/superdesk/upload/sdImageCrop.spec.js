'use strict';

describe('Image Crop', function() {

    beforeEach(module('superdesk.upload'));
    beforeEach(module('superdesk.imageFactory'));

    describe('sdImageCrop directive', function() {
        var scope, isoScope, fakeImg, $elm;
        var url = 'http://master.dev.superdesk.org/api/upload/55dbf92936b0650033518780/raw?_schema=http';
        var newUrl = 'http://master.dev.superdesk.org/api/upload/55ca5972b8e27e006385b6e3/raw?_schema=http';

        beforeEach(inject(function ($rootScope, imageFactory, $compile) {
            scope = $rootScope.$new();

            fakeImg = {};
            spyOn(imageFactory, 'makeInstance').and.callFake(function () {
                return fakeImg;
            });

            scope.boxWidth = 800;
            scope.boxHeight = 600;
            scope.src = url;
            scope.rendition = {width: 800, height: 600};
            scope.original = {width: 900, height: 600};
            scope.cropData = {};
            $elm = $compile('<div sd-image-crop data-src="src" data-show-Min-Size-Error="true"' +
                ' data-original="original" ' +
                ' data-rendition="rendition" data-box-width="boxWidth"' +
                ' data-box-height="boxHeight" crop-data="cropData"></div>')(scope);
        }));

        it('invokes watch', inject(function() {
            scope.$digest();
            expect(fakeImg.src).toEqual(url);
        }));

        it('observes changes', inject(function() {
            scope.$digest();

            isoScope = $elm.isolateScope();
            isoScope.src = newUrl;
            isoScope.$digest();

            expect(fakeImg.src).toEqual(newUrl);
        }));

        it('defines image onload handler', inject(function() {
            scope.$digest();

            isoScope = $elm.isolateScope();
            isoScope.src = newUrl;
            isoScope.$digest();

            expect(typeof fakeImg.onload).toEqual('function');
        }));

        describe('onload handler', function() {
            var mySpy;
            beforeEach(inject(function() {
                mySpy = jasmine.createSpy('mySpy');
                spyOn(window, '$').and.callFake(function () {
                    var fakeObj = {
                        'Jcrop': mySpy
                    };
                    return fakeObj;
                });
            }));

            it('executes with validation passed', inject(function() {
                scope.minimumSize = [scope.boxWidth, scope.boxHeight];
                scope.$digest();

                isoScope = $elm.isolateScope();
                isoScope.src = newUrl;
                isoScope.$digest();

                expect(typeof fakeImg.onload).toEqual('function');

                var handler = fakeImg.onload;
                handler.apply(fakeImg);
                expect(mySpy.calls.count()).toEqual(1);

                var retObj = mySpy.calls.argsFor(0);
                expect(retObj[0].aspectRatio).toBe(4 / 3);
                expect(retObj[0].boxWidth).toBe(800);
                expect(retObj[0].boxHeight).toBe(600);
                expect(retObj[0].minSize).toEqual([800, 600]);
                expect(retObj[0].trueSize).toEqual([900, 600]);
                expect(retObj[0].setSelect).toEqual([50, 0, 850, 600]);
            }));

            it('executes with validation failed', inject(function($compile) {
                scope.original.width = 500;
                scope.$digest();

                isoScope = $elm.isolateScope();
                isoScope.src = newUrl;
                isoScope.$digest();

                expect(typeof fakeImg.onload).toEqual('function');

                var handler = fakeImg.onload;
                handler.apply(fakeImg);
                expect(mySpy.calls.count()).toEqual(0);
                expect($elm.text())
                    .toBe('Sorry, but image must be at least ' + scope.rendition.width + 'x' + scope.rendition.height +
                          ', (it is 500x600).');
            }));
        });
    });
});
