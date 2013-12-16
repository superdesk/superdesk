'use strict';

module.exports = function (grunt) {
  // load all grunt tasks
  require('matchdep').filterDev('grunt-*').forEach(grunt.loadNpmTasks);

  var config = {
    app: 'app',
    dist: 'dist',
    serverURL: grunt.option('server') || 'http://localhost:5000',
    livereload: 35729
  };

  try {
    yeomanConfig.app = require('./bower.json').appPath || config.app;
  } catch (e) {}

  grunt.initConfig({
    pkg: grunt.file.readJSON('./package.json'),
    yeoman: config,

    less: {
      development: {
        options: {
          paths: ['app/styles/less'],
          yuicompress: true
        },
        files: {
          'app/styles/css/bootstrap.css': 'app/styles/less/bootstrap.less'
        }
      }
    },

    watch: {
      livereload: {
        options: {
          livereload: config.livereload
        },
        files: [
          '<%= yeoman.app %>/{,*/}*.html',
          '{.tmp,<%= yeoman.app %>}/styles/css/custom.css',
          '{.tmp,<%= yeoman.app %>}/styles/{,*/}*.less',
          '{.tmp,<%= yeoman.app %>}/{,*/}*.js',
          '<%= yeoman.app %>/images/{,*/}*.{png,jpg,jpeg,gif,webp,svg}'
        ],
        tasks: ['less']
      }
    },

    connect: {
      options: {
        port: 9000,
        hostname: 'localhost',
      },
      server: {
        options: {
          livereload: config.livereload,
          base: [
            '<%= yeoman.dist %>',
            '<%= yeoman.app %>'
          ]
        }
      }
    },

    open: {
      server: {
        url: 'http://localhost:<%= connect.options.port %>'
      }
    },

    clean: {
      dist: {
        files: [{
          dot: true,
          src: [
            '.tmp',
            '<%= yeoman.dist %>/*',
            '!<%= yeoman.dist %>/.git*'
          ]
        }]
      },
      server: '.tmp'
    },

    jshint: {
      options: {
        jshintrc: '.jshintrc',
      },
      all: [
        //'Gruntfile.js',
        '<%= yeoman.app %>/scripts/main.js',
        '<%= yeoman.app %>/scripts/superdesk/**/*.js',
        '<%= yeoman.app %>/scripts/superdesk-*/**/*.js'
      ]
    },

    karma: {
      unit: {
        configFile: 'karma.conf.js',
        singleRun: false,
        autoWatch: true
      }
    },

    copy: {
      dist: {
        files: [{
          expand: true,
          dot: true,
          cwd: '<%= yeoman.app %>',
          dest: '<%= yeoman.dist %>',
          src: [
            '.htaccess',
            '*.{ico,txt}',
            'images/**/*',
            'styles/{,*/}*.css',
            'scripts/**/*.{html,js,css,jpg,jpeg,png,gif,json}',
            'template/**/*.html',
            'config.js'
          ]
        }]
      }
    },

    compress: {
      build: {
        options: {archive: 'dist/<%= pkg.name %>.zip', mode: 'zip'},
        src: ['**'], cwd: '<%= yeoman.dist %>', expand: true, dot: true, dest: '<%= pkg.name %>/'
      }
    },

    nggettext_extract: {
      pot: {
        files: {
          'po/superdesk.pot': '<%= yeoman.app %>/scripts/superdesk/**/*.{html,js}'
        }
      }
    },

    nggettext_compile: {
      all: {
        files: {
          '<%= yeoman.app %>/scripts/translations.js': 'po/*.po'
        }
      }
    },

    requirejs: {
      compile: {
        options: {
          baseUrl: '<%= yeoman.app %>/scripts',
          mainConfigFile: '<%= yeoman.app %>/scripts/main.js',
          out: '<%= yeoman.dist %>/scripts/main.js',
          name: 'main'
        }
      }
    },

    template: {
      local: {
        options: {
          data: {
            server: {
              url: config.serverURL
            }
          }
        },
        files: {
          '<%= yeoman.dist %>/index.html': '<%= yeoman.app %>/index.html'
        }
      }
    }
  });

  grunt.registerTask('server', [
    'clean:dist',
    'clean:server',
    'less',
    'template',
    'connect:server',
    'open',
    'watch'
  ]);

  grunt.registerTask('test', [
    'clean:server',
    'karma'
  ]);

  grunt.registerTask('build', [
    'clean:dist',
    'jshint',
    'less',
    'template',
    'copy'
  ]);

  grunt.registerTask('default', ['build']);
  grunt.registerTask('package', ['build', 'compress']);
};
