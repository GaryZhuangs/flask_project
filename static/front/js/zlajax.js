// 对jquery的ajax的封装

'use strict';
var zlajax = {
	'get':function(args) {
		args['method'] = 'get';
		this.ajax(args);
	},
	'post':function(args) {
		args['method'] = 'post';
		this.ajax(args);
	},
	'ajax':function(args) {
		// 设置csrftoken
		this._ajaxSetup();
		$.ajax(args);
	},
	'_ajaxSetup': function() {
		$.ajaxSetup({
			'beforeSend':function(xhr,settings) {
				if (!/^(GET|HEAD|OPTIONS|TRACE)$/i.test(settings.type) && !this.crossDomain) {
                    var csrftoken = $('meta[name=csrf-token]').attr('content');
					
                    xhr.setRequestHeader("X-CSRFToken", csrftoken)
                }
			}
		});
	}
};
document.querySelector('.navbar-header').addEventListener('mousemove', function(e) {
  const x = e.pageX - this.offsetLeft;
  const y = e.pageY - this.offsetTop;
  this.style.setProperty('--x', `${x}px`);
  this.style.setProperty('--y', `${y}px`);
});