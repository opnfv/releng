'use strict';


describe('testing the Pods page for unauthorized user', function () {

	it( 'should navigate to pods link ', function() {
		browser.get('http://0.0.0.0:8000/');
		var nortonlink = element(by.linkText('Pods')).click();
		var EC = browser.ExpectedConditions;
		browser.wait(EC.urlContains('http://0.0.0.0:8000/#/pods'), 8000);
	});

	it('create button is not visible for unauthorized user', function () {
		browser.get('http://0.0.0.0:8000/#/pods');
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
		expect(pod.isPresent()).toBeFalsy();
	});

});
