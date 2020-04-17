module.exports = function(grunt) {
    require('superdesk-core/Gruntfile')(grunt);
    grunt.config.set('nggettext_compile.all.files.0.cwd', './po');
};
