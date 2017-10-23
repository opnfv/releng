exports.config = {
	seleniumAddress: 'http://localhost:4444/wd/hub',
	capabilities: {
		'browserName': 'chrome',
		'chromeOptions': {
			'args': ['show-fps-counter=true', '--disable-web-security', "no-sandbox", "--headless", "--disable-gpu"]
		}
	},
	jasmineNodeOpts: {
		showColors: true,
		defaultTimeoutInterval: 30000
	}
};



