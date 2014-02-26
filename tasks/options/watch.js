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
        options: {
            livereload: true
        },
        files: [
            '<%= appDir %>/scripts/**/*.html',
            '<%= appDir %>/scripts/**/*.js'
        ],
        tasks: ['ci']
    }
};
