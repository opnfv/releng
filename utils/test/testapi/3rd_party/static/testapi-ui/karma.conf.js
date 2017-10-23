module.exports = function (config) {
	config.set({
		frameworks: ['jasmine'],
		files: [
			"assets/lib/angular/angular.js",
			"assets/lib/angular-mocks/angular-mocks.js",
		],
		autoWatch: true,
		browsers: ['Chrome'],
		singleRun: true,
		reporters: ['progress', 'coverage'],
        preprocessors: { 'src/*.js': ['coverage'] }
	});
};
