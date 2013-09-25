
module.exports = function(grunt) {
    grunt.registerMultiTask('write', 'write content to a file', function(){
        grunt.file.write(this.data.file, this.data.content);
        grunt.log.ok('wrote to ' + this.data.file);
    }); 
};