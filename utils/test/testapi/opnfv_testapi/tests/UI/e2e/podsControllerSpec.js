'use strict';

var mock = require('protractor-http-mock');
var baseURL = "http://localhost:8000"
describe('testing the Pods page for unauthorized user', function () {

	beforeEach(function(){
		mock([{
			request: {
			  path: '/api/v1/pods',
			  method: 'GET'
			},
			response: {
				data: {
					pods: [{role: "community-ci", name: "test", owner: "testUser", details: "DemoDetails", mode: "metal", _id: "59f02f099a07c84bfc5c7aed", creation_date: "2017-10-25 11:58:25.926168"}]
				}
			}
		  }]);
	});

	afterEach(function(){
		mock.teardown();
	});

	it( 'should navigate to pods link ', function() {
		browser.get(baseURL);
		var nortonlink = element(by.linkText('Pods')).click();
		var EC = browser.ExpectedConditions;
		browser.wait(EC.urlContains(baseURL+ '/#/pods'), 10000);
	});

	it('create button is not visible for unauthorized user', function () {
		browser.get(baseURL+'#/pods');
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
		expect(pod.isPresent()).toBe(true);
	});

	it('Show details results when click the link',function() {
		expect(element(by.css('.show-pod.hidden')).isPresent()).toBe(true);
		var nortonlink = element(by.linkText('test')).click();
		expect(element(by.css('.show-pod.hidden')).isPresent()).toBe(false);
	});

	it('Hide details results when click the link',function() {
		expect(element(by.css('.show-pod.hidden')).isPresent()).toBe(false);
		var nortonlink = element(by.linkText('test')).click();
		expect(element(by.css('.show-pod.hidden')).isPresent()).toBe(true);
	});

});

describe('testing the Pods page for authorized user', function () {

	beforeEach(function(){
		mock([
			{
				request: {
				  path: '/api/v1/pods',
				  method: 'POST'
				},
				response: {
					data: {
						href: baseURL+"/api/v1/pods/test"
					}
				}
			  },
			  {
				request: {
				path: '/api/v1/profile',
				method: 'GET'
				},
				response: {
					data: {
						"fullname": "Thuvarakan Tharmarajasingam", "_id": "59f02eef9a07c84bfc5c7aec", "user": "thuva4", "groups": ["opnfv-testapi-users", "opnfv-gerrit-lsoapi-contributors", "opnfv-gerrit-functest-contributors"], "email": "tharma.thuva@gmail.com"
					}
				}
			}
		]);
	});

	it('create button is visible for authorized user', function () {
		browser.get(baseURL + '/#/pods');
		var buttonCreate = element(by.buttonText('Create'));
		expect(buttonCreate.isDisplayed()).toBe(true);
	});

	it('Do not show error if input is acceptable', function () {
		var name = element(by.model('ctrl.name'));
		var details = element(by.model('ctrl.details'));
		name.sendKeys('test');
		details.sendKeys('DemoDetails');
		var buttonCreate = element(by.buttonText('Create'));
		buttonCreate.click();
		expect(element(by.css('.alert.alert-danger.ng-binding.ng-scope')).isDisplayed()).toBeFalsy();
	});

	it('Show error when user click the create button with a empty name', function () {
		browser.get(baseURL+ '/#/pods');
		var details = element(by.model('ctrl.details'));
		details.sendKeys('DemoDetails');
		var buttonCreate = element(by.buttonText('Create'));
		buttonCreate.click();
		expect(element(by.cssContainingText(".alert","Name is missing.")).isDisplayed()).toBe(true);
	});

})