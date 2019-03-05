const QTYPE = ['qStatus', 'qData', 'qFlow'];

function remove_question(event) {
  var container = $(this).parent().parent();
  $(this).parent().detach();
  var items = $('.input-group', container);
  for (var i = 0; i < items.length; i++) {
    var item = items[i];
    $('.input-group-text', $(item)).text(i+1);
  }
  event.preventDefault();
}

$('.q-add').click(function (event) {
  event.preventDefault();
  var row = $(this).parent().parent();
  var container = $('td', row);
  var count = $('.input-group', row).length;
  var name = $('.input-group input', row).attr('name');
  var element = $('<div class="input-group"><button class="btn btn-sm btn-danger">X</button><div class="input-group-prepend"><span class="input-group-text">' + (count + 1) + '</span></div><input type="text" name="' + name + '" class="form-control" /></div>');
  $('button', element).click(remove_question);
  element.appendTo(container);
});

$('.input-group>button').click(remove_question);

$('input[type="submit"]').click(function (event) {
  $('.alert.alert-danger').detach();
  for (var i in QTYPE) {
    var qtype = QTYPE[i];
    var count = 0;
    $('#' + qtype + ' input').each(function (index, elem) {
      $(elem).val($(elem).val().trim());
      if ($(elem).val() === '') {
        $(elem).parent().detach();
      } else {
        count++;
      }
    });
    if (count === 0) {
      var element = $('<div class="input-group"><button class="btn btn-sm btn-danger">X</button><div class="input-group-prepend"><span class="input-group-text">' + (count + 1) + '</span></div><input type="text" name="' + name + '" class="form-control" /></div>');
      var container = '#' + qtype + '>td';
      $('<p class="alert alert-danger mb-1 p-1" role="alert">至少要定義一個問題！</p>').appendTo(container);
      $('button', element).click(remove_question);
      element.appendTo(container);
      event.preventDefault();
    }
  }
});