odoo.define('website_notify.email_notify', function(require) {
	"use strict";
	var base = require('web_editor.base');
	var core = require('web.core');
	var sale = require('website_sale.cart');
	var ajax = require('web.ajax');
	var _t = core._t;
	$("#email_notification").on("click", function(){
		var email = $('#email').val();
		var name = $('#p_name').val();
		console.log('email:' + email);
		ajax.jsonRpc("/shop/notifybyemail", 'call', {
			'email' : email, 'product': name
		}).then(function(data) {
			var msg = $('.notify_msg');
			var notify_me = $('.notify_me');
			var email = $('#email');
			var notify = $("#email_notification");
			msg.show();
			email.hide();
			notify_me.hide();
			notify.hide();
			return false;
		});
	});
});