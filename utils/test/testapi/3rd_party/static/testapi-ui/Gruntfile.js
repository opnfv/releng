
module.exports = function (grunt) {
	require('load-grunt-tasks')(grunt);
	require('grunt-protractor-coverage')(grunt);
	grunt.loadNpmTasks('grunt-shell-spawn');
	grunt.loadNpmTasks('grunt-wait');
	grunt.loadNpmTasks('grunt-contrib-copy');


	grunt.initConfig({
		copy: {
			assets: {
			  expand: true,
			  cwd: 'assets',
			  src: '**',
			  dest: 'testapi-ui/assets',
			},
			components: {
				expand: true,
				cwd: 'components',
				src: '**',
				dest: 'testapi-ui/components',
			},
			shared: {
				expand: true,
				cwd: 'shared',
				src: '**',
				dest: 'testapi-ui/shared',
			},
			filesPng: {
				expand: true,
				// cwd: '*.png',
				src: '*.png',
				dest: 'testapi-ui/',
			},
			filesIco: {
				expand: true,
				// cwd: '*.ico',
				src: '*.ico',
				dest: 'testapi-ui/',
			},
			filesJs: {
				expand: true,
				// cwd: 'app.js',
				src: 'app.js',
				dest: 'testapi-ui/',
			},
			filesJson: {
				expand: true,
				// cwd: 'app.js',
				src: 'config.json',
				dest: 'testapi-ui/',
			}
		},
		wait: {
			default: {
				options: {
					delay: 1000
				}
			}
		},
		shell: {
			updateSelenium: {
				command: 'node_modules/protractor/bin/webdriver-manager update',
				options: {
		      		async: false
		    	}
			},
			startSelenium: {
				command: 'node_modules/protractor/bin/webdriver-manager start',
				options: {
			      async: true
			    }
			},
			startServer:{
				command: 'python -m SimpleHTTPServer 8000',
				options: {
			      async: true
			    }
			},
			options: {
		        stdout: false,
		        stderr: false
		    }
		},
		instrument: {
	        files: ['components/**/*.js'],
	        options: {
	        lazy: false,
	            basePath: "./testapi-ui/"
	        }
	    },   
		karma: {
			unit: {
				configFile: 'karma.conf.js'
			}
		},
		protractor_coverage: {
		    options: {
		        keepAlive: true,
		        noColor: false,
		        coverageDir: '../../../opnfv_testapi/tests/UI/test/coverage',
		        args: {
		            // baseUrl: 'http://localhost:8000',
		            specs: ['../../../opnfv_testapi/tests/UI/test/e2e/podsControllerSpec.js']
		        }
		    },
		    local: {
		        options: {
		            configFile: 'protractor-conf.js'
		        }
		    }
		},
		makeReport: {
	        src: '../../../opnfv_testapi/tests/UI/test/coverage/*.json',
	        options: {
	            print: 'detail'
	        }
	    },
		protractor: {
			e2e: {
				options: {
					args: {
						specs: ['../../../opnfv_testapi/tests/UI/test/e2e/podsControllerSpec.js']
					},
					configFile: 'protractor-conf.js',
					keepAlive: true
				}
			}
		}
	});
	grunt.registerTask('test', [
		'karma:unit'
	]);
	grunt.registerTask('e2e', [
		'copy:assets',
		'copy:components',
		'copy:shared',
		'copy:filesPng',
		'copy:filesIco',
		'copy:filesJs',
		'copy:filesJson',
		'instrument',
		'shell:startServer',
		'shell:updateSelenium',
		'shell:startSelenium',
		'wait:default',
		'protractor_coverage',
		'makeReport',
		// 'protractor'
	]);
}
