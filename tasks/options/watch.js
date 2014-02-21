module.exports = {
    options: {
        livereload: '<%= livereloadPort %>',
    },
    less: {
        files: [
            '{<%= tmpDir %>,<%= appDir %>}/styles/{,*/}*.less'
        ],
        tasks: ['less']
    },
    code: {
        files: [
            '<%= appDir %>/scripts/**/*.html',
            '<%= appDir %>/scripts/**/*.js'
        ],
        options: {
            livereload: true
        }
    }
};
