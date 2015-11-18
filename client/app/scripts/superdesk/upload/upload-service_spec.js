define(['./upload-service'], function(UploadService) {
    'use strict';

    describe('upload service', function() {

        beforeEach(module(function($provide) {
            $provide.service('upload', UploadService);
            $provide.service('$upload', ['$q', function($q) {
                // angular-file-upload api
                this.upload = function() {
                    return $q.when();
                };
                this.http = function() {};
            }]);
        }));

        it('can start uploading', inject(function(upload, $upload) {
            var config = {url: 'test', method: 'POST', data: 'test'};
            spyOn($upload, 'upload').and.callThrough();
            upload.start(config);
            expect($upload.upload).toHaveBeenCalledWith(config);
        }));

        it('can restart uploading', inject(function(upload, $upload) {
            var config = {};
            spyOn($upload, 'http');
            upload.restart(config);
            expect($upload.http).toHaveBeenCalledWith(config);
        }));

        it('should know that config after calling start is an upload', inject(function(upload) {
            var config = {};
            upload.start(config);
            expect(upload.isUpload(config)).toBe(true);
        }));

        it('should know that config without using start is not an upload', inject(function(upload) {
            expect(upload.isUpload({})).toBe(false);
        }));
    });
});
