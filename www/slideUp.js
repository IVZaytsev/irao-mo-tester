$(document).ready(function() {
	$(document).find('thead').addClass("collapsed");
	
	$(".nfcsubmit").submit(function(event) {
		event.preventDefault();
		
		$.ajax({
			url: 'http://127.0.0.1:8080/',
			type: 'POST',
			contentType: 'application/json',
			dataType: 'json',
			async: true,
			data: JSON.stringify({
				id: $(this.getElementsByTagName('input'))[0].value,
				number: $(this.getElementsByTagName('input'))[1].value,
				desc: $(this.getElementsByTagName('input'))[2].value
			})
		});
	});
	
	$('.flip').click(function() {
		if($(this).hasClass("collapsed")) {
			$(this.closest('table')).find('tbody').find('td').slideDown('fast');
			$(this.closest('table')).find('tbody').toggle('fast');
			$(this.closest('table')).find('tbody').css('display', 'table-row');
			$(this).removeClass("collapsed");
		} else {
			$(this.closest('table')).find('tbody').find('td').slideUp('fast');
			$(this.closest('table')).find('tbody').toggle('fast');
			$(this.closest('table')).find('tbody').css('display', 'none');
			$(this).addClass("collapsed");
		}
	});
})