'use strict';

var mock = require('protractor-http-mock');

describe('testing the Pods page for unauthorized user', function () {
	
	beforeEach(function(){
		var hello = "Hello world";
		mock([{
			request: {
			  path: '/api/v1/pods',
			  method: 'GET'
			},
			response: {
				data: {
					pods: [{role: "community-ci", name: "thuva", owner: "thuva4", details: "cdsfds", mode: "metal", _id: "59f02f099a07c84bfc5c7aed", creation_date: "2017-10-25 11:58:25.926168"}]
				}
			}
		  }]);
	});

	afterEach(function(){
		mock.teardown();
	});
	

	it( 'should navigate to pods link ', function() {
		browser.get('http://localhost:8000/');
		var nortonlink = element(by.linkText('Pods')).click();
		var EC = browser.ExpectedConditions;
		browser.wait(EC.urlContains('http://localhost:8000/#/pods'), 8000);
	});

	it('create button is not visible for unauthorized user', function () {
		browser.get('http://localhost:8000/#/pods');
		var buttonCreate = element(by.buttonText('Create'));
		expect(buttonCreate.isDisplayed()).toBeFalsy();
	});

	it('filter button is not visible for unauthorized user', function () {
		var buttonFilter = element(by.buttonText('Filter'));
		expect(buttonFilter.isDisplayed()).toBe(true)
	});

	it('clear button is not visible for unauthorized user', function () {
		var buttonClear = element(by.buttonText('Clear'));
		expect(buttonClear.isDisplayed()).toBe(true)
	});

	it('Show results when click filter button', function () {
		var buttonFilter = element(by.buttonText('Filter'));
		buttonFilter.click();
		var pod = element(by.css('.show-pod'));
		var firstUsername = element(by.repeater('(index, pod) in ctrl.data.pods')
				.row(0).column(0));
		expect(pod.isPresent()).toBe(true);   
	});

});
