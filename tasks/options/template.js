
module.exports = function(grunt) {
    return {
        options: {
            data: {server: {url: grunt.option('server') || 'http://superdesk.apiary.io'}}
        },
        apiary: {
            files: {'<%= distDir %>/index.html': '<%= appDir %>/index.html'},
        }
    };
};
