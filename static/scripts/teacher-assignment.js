const QTYPE = ['qStatus', 'qData', 'qFlow'];

$('.q-add').click(function(event) {
    event.preventDefault();
    var row = $(this).parent().parent();
    var container = $('td', row);
    var count = $('.input-group', row).length;
    var name = $('.input-group input', row).attr('name');
    $('<div class="input-group"><div class="input-group-prepend"><span class="input-group-text">'+(count+1)+'</span></div><input type="text" name="'+name+'" class="form-control" /></div>').appendTo(container);
});

$('input[type="submit"]').click(function(event) {
    $('.alert.alert-danger').detach();
    for(var i in QTYPE) {
        var qtype = QTYPE[i];
        var count = 0;
        $('#'+qtype+' input').each(function(index, elem) {
            $(elem).val($(elem).val().trim());
            if ($(elem).val() === '') {
                $(elem).parent().detach();
            } else {
                count++;
            }
        });
        if (count === 0) {
            $('<div class="input-group"><div class="input-group-prepend"><span class="input-group-text">'+(count+1)+'</span></div><input type="text" name="'+name+'" class="form-control" /></div>').appendTo('#'+qtype+'>td');
            $('<div class="alert alert-danger mb-0 mt-1 p-1" role="alert">至少要定義一個問題！</div>').appendTo('#'+qtype+'>td');
            event.preventDefault();
        }
    }
});