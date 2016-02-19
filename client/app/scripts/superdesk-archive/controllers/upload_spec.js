define(['./upload'], function(UploadController) {
    'use strict';

    describe('Upload controller', function() {

        var files = [{type: 'text/plain'}],
            UPLOAD_URL = 'upload_url';

        beforeEach(module(function($provide) {
            $provide.service('api', function($q) {
                return {
                    archive: {
                        getUrl: function() {
                            return $q.when(UPLOAD_URL);
                        },
                        getHeaders: function() {
                            return {};
                        },
                        update: function(dest, diff) {
                            return $q.when({});
                        }
                    }
                };
            });

            $provide.service('upload', function($q) {
                this.start = function(config) {
                    this.defer = $q.defer();
                    return this.defer.promise;
                };
            });

            $provide.service('archiveService', function() {
                this.addTaskToArticle = function(item) {
                };
            });
        }));
        beforeEach(inject(function (session) {
            session.identity = {_id: 'user:1', byline: 'Admin'};
        }));

        it('can upload files when added', inject(function($controller, $rootScope, $q, api, upload) {
            var scope = $rootScope.$new(true);

            spyOn(upload, 'start').and.callThrough();

            scope.resolve = function() {};
            var resolve = spyOn(scope, 'resolve');

            $controller(UploadController, {$scope: scope});

            $rootScope.$digest();

            expect(scope.items.length).toBe(0);

            scope.addFiles(files);

            $rootScope.$digest();

            expect(scope.items.length).toBe(1);
            expect(scope.items[0].file.type).toBe('text/plain');
            expect(scope.items[0].meta).not.toBe(undefined);
            expect(scope.items[0].progress).toBe(0);

            // mandatory fields
            scope.items[0].meta.headline = 'headline text';
            scope.items[0].meta.slugline = 'slugline text';
            scope.items[0].meta.description_text = 'description';

            scope.save();
            $rootScope.$digest();

            expect(upload.start).toHaveBeenCalledWith({
                method: 'POST',
                url: UPLOAD_URL,
                data: {media: files[0]},
                headers: api.archive.getHeaders()
            });

            upload.defer.notify({
                total: 100,
                loaded: 50
            });

            $rootScope.$digest();

            expect(scope.items[0].progress).toBe(50);

            upload.defer.resolve({data: {}});
            $rootScope.$digest();

            expect(resolve).toHaveBeenCalledWith([{}]);
        }));

        it('can display error message if any of metadata field missing',
            inject(function($controller, $rootScope, $q, api, upload) {
            var scope = $rootScope.$new(true);

            $controller(UploadController, {$scope: scope});
            $rootScope.$digest();
            expect(scope.items.length).toBe(0);

            scope.addFiles(files);
            $rootScope.$digest();

            scope.errorMessage = null;

            // missed meta.description field on purpose
            scope.items[0].meta.headline = 'headline text';
            scope.items[0].meta.slugline = 'slugline text';

            expect(scope.errorMessage).toBe(null);

            scope.save();
            $rootScope.$digest();
            expect(scope.errorMessage).toBe('Required field(s) are missing');
        }));
        it('can try again to upload when try again is clicked',
            inject(function($controller, $rootScope, $q, api, upload) {
            var scope = $rootScope.$new(true);

            spyOn(upload, 'start').and.callThrough();

            scope.resolve = function() {};

            $controller(UploadController, {$scope: scope});
            $rootScope.$digest();
            expect(scope.items.length).toBe(0);

            scope.addFiles(files);
            $rootScope.$digest();

            expect(scope.items.length).toBe(1);
            expect(scope.items[0].file.type).toBe('text/plain');
            expect(scope.items[0].meta).not.toBe(undefined);
            expect(scope.items[0].progress).toBe(0);

            // mandatory fields
            scope.items[0].meta.headline = 'headline text';
            scope.items[0].meta.slugline = 'slugline text';
            scope.items[0].meta.description_text = 'description';

            scope.failed = true;
            scope.tryAgain();
            $rootScope.$digest();

            expect(upload.start).toHaveBeenCalledWith({
                method: 'POST',
                url: UPLOAD_URL,
                data: {media: files[0]},
                headers: api.archive.getHeaders()
            });

        }));
    });

});
