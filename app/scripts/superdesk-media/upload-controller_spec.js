define(['./upload-controller'], function(UploadController) {
    'use strict';

    describe('Upload controller', function() {

        var files = [{type: 'text/plain'}],
            UPLOAD_URL = 'upload_url';

        beforeEach(module(function($provide) {
            $provide.service('api', function($q) {
                return {
                    image: {
                        getUrl: function() {
                            return $q.when(UPLOAD_URL);
                        },
                        getHeaders: function() {
                            return {};
                        },
                        update: function(dest, diff) {
                            return $q.when({data: {}});
                        }
                    }
                };
            });
        }));

        it('can upload files when added', inject(function($controller, $rootScope, $q, api) {
            var scope = $rootScope.$new(true),
                defer;

            var $upload = {
                upload: function() {
                    defer = $q.defer();
                    return defer.promise;
                }
            };

            var upload = spyOn($upload, 'upload').andCallThrough();

            scope.resolve = function() {};
            var resolve = spyOn(scope, 'resolve');

            $controller(UploadController, {
                $upload: $upload,
                $scope: scope,
                api: api
            });

            $rootScope.$digest();

            expect(scope.items.length).toBe(0);

            scope.addFiles(files);

            $rootScope.$digest();

            expect(upload).toHaveBeenCalledWith({
                method: 'POST',
                url: UPLOAD_URL,
                file: files[0],
                isUpload: true,
                headers: api.image.getHeaders()
            });

            expect(scope.items.length).toBe(1);
            expect(scope.items[0].file.type).toBe('text/plain');
            expect(scope.items[0].meta).not.toBe(undefined);
            expect(scope.items[0].progress).toBe(0);

            defer.notify({
                total: 100,
                loaded: 50
            });

            $rootScope.$digest();

            expect(scope.items[0].progress).toBe(50);

            scope.items[0].meta.Description = 'test';

            var result;
            scope.save().then(function(_result) {
                result = _result;
            });

            $rootScope.$digest();

            expect(result).toBe(undefined);
            defer.resolve({});

            $rootScope.$digest();

            expect(result.length).toBe(1);
            expect(resolve).toHaveBeenCalledWith(result);
        }));
    });

});
