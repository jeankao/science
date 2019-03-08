$(function () {
  //
  // flow editor
  //
  const CS_INPUT = 0,
        CS_OUTPUT = 1,
        CS_LOOP = 2,
        CS_IF = 3, 
        CS_PROCESS = 4;

  const FLOW_TYPE_LABEL = ["輸入", "輸出", "迴圈", "判斷", "處理"];
  const FLOW_TYPE_CLASS = ["input", "output", "loop", "if", "process"];

  const EXT_BLOCKS = [CS_LOOP, CS_IF];

  const CLASS_TYPE = {
    'input': CS_INPUT, 
    'output': CS_OUTPUT, 
    'loop': CS_LOOP, 
    'if': CS_IF, 
    'process': CS_PROCESS,
  };

  $('.flow-container').sortable({
    placeholder: 'ui-state-highlight',
  });

  function _new_flow_item(type, content, container, criteria = '') {
    var label = FLOW_TYPE_LABEL[type];
    var flow_type_class = FLOW_TYPE_CLASS[type];
    var flow_components;
    if (!EXT_BLOCKS.includes(type)) {
      flow_components = '<textarea class="form-control" placeholder="請輸入流程說明文字...">'+content+'</textarea>';
    } else {
      flow_components = '<div class="flow-group"><input type="text" class="form-control" placeholder="請輸入'+label+'條件..." value="'+criteria+'" /><div class="new-flow-op"><button class="btn btn-sm btn-dark disabled">新增流程 &gt; </button><div class="new-flow-type"><button class="btn btn-sm btn-outline-dark new-flow-process">處理</button><button class="btn btn-sm btn-outline-dark new-flow-input">輸入</button><button class="btn btn-sm btn-outline-dark new-flow-output">輸出</button><button class="btn btn-sm btn-outline-dark new-flow-loop">迴圈</button><button class="btn btn-sm btn-outline-dark new-flow-if">判斷</button></div></div><div class="flow-container"></div></div>';
    }
    var flow = $('<div class="flow-item '+ flow_type_class +'"><div class="flow-content"><div class="label-op"><span class="badge badge-dark">'+label+'</span><span class="badge badge-danger flow-delete">刪除</span></div>'+ flow_components +'</div></div>');
    $(".flow-content", flow).prepend($('<span class="ui-icon ui-icon-arrow-4"></span>'));
    $('.flow-container', flow).sortable({
      placeholder: 'ui-state-highlight',
    });
    if (EXT_BLOCKS.includes(type)) {
      $('.new-flow-op', flow).click(_new_flow_item_handler);
      var my_container = $('.flow-container', flow);
      for (var i = 0; i < content.length; i++) {
        var item = content[i];
        _new_flow_item(item.type, item.content, my_container, EXT_BLOCKS.includes(item.type) ? item.criteria : '');
      }
    }
    flow.appendTo(container);
    $($('textarea', flow)[0]).focus();
    $('.flow-delete').click(function(event) {
      $(this).parent().parent().parent().detach();
    });
  }

  function _new_flow_item_handler(event) {
    var container = $(this.nextElementSibling);
    var button = $(event.target);
    var classtype = button.attr('class').match(/new-flow-([^ ]+)/);

    if (classtype.length == 2) {
      _new_flow_item(CLASS_TYPE[classtype[1]], '', container);
    }
  }

  $('.new-flow-op').click(_new_flow_item_handler);

  $('#flow-submit').click(function(event) {
    function _collect_flow_items(container) {
      var children = $(container).children();
      var count = children.length;
      var data = [];
      for (var i = 0; i < count; i++) {
        var item = $(children[i]);
        var classtype = item.attr('class').split(' ');
        var type = CLASS_TYPE[classtype[1]];
        if (EXT_BLOCKS.includes(type)) {
          data.push({
            type: type,
            criteria: $('input[type="text"]', item).val(),
            content: _collect_flow_items($('.flow-container', item).get(0)),
          });
        } else {
          data.push({
            type: type,
            content: $('textarea', item).val(),
          });
        }
      }
      return data;
    }
    var data = _collect_flow_items('#flow-list');
    $('#flow-form input[name="jsonstr"]').val(JSON.stringify(data));
    $('#flow-form').submit();
  });

  function initFlowElements(hid=0) {
    var curr_qid = $('#flow-form input[name="qid"]').val();
    var flowjson;
    try {
      flowjson = flowdata['q'+curr_qid][hid].expr;
    } catch (error) {
      flowjson =[];
    }
    var items = flowjson;
    var size = items.length;

    for (var i = 0; i < size; i++) {
      item = items[i];
      _new_flow_item(item.type, item.content, '#flow-list', EXT_BLOCKS.includes(item.type) ? item.criteria : '');
    }
  }
  //-------------------------------------------------------------------------
  //
  // expression editor
  //
  const CS_VAR = 'btn-warning',
        CS_ARR = 'btn-danger',
        CS_CONST = 'btn-success',
        CS_SYMBOL = 'btn-default',
        CS_OP = 'btn-info';

  const TYPEMAP = {
    'arr': {c: CS_ARR, reg: /[\w]+(\[[^\[\]]+\])+/},
    'str-const': {c: CS_CONST, reg: /^'[^\']*'$/},
    'num-const': {c: CS_CONST, reg: /^\d+$/},
    'op': {c: CS_OP, reg: /[\(\)+\-*\/^]/},
    'symbol': {c: CS_SYMBOL, reg: /[\[\],]/},
    'var': {c: CS_VAR, reg: /.+/},
  };

  var $modal_literal_value = $('#modal-literal-value'),
      $modal_new_array = $('#modal-new-array'),
      $modal_new_var = $('#modal-new-var');

  $('th', $modal_new_array).each(function(index, item) {
    $(item).html('<span class="badge badge-dark">'+$(item).text()+'</span>');
  });

  function getType(token) {
    if (Number.isInteger(token))
      return 'num-const';
    for (type in TYPEMAP) {
      if (token.match(TYPEMAP[type].reg))
        return type;
    }
    return 'var';
  }

  function _new_arr_expr_block(item_str, parent) {
    var container = $('<ul class="expr-rhs expr-item-list"></ul>');
    var tokens = item_str.match(/\w+|[\(\)+\-*\/^]/g);
    for (var i = 0; i < tokens.length; i++)
      newBlock(getType(tokens[i].trim()), tokens[i].trim(), container);
    container.appendTo(parent);
  }

  function newBlock(type, item, target, add_container = false) {
    var element = $('<li class="expr-item '+type+' '+TYPEMAP[type].c+'"></li>');
    if (type !== 'symbol')
      element.addClass('btn btn-sm');
    if (type === 'arr' && add_container) {
      var name = item.match(/[^\[\]]+/g);
      if (name && name.length > 1) {
        element.append(name[0]);
        for (var i = 1; i < name.length; i++) {
          element.append('[');
          _new_arr_expr_block(name[i], element);
          element.append(']');
        }
      }
    } else {
      element.append(item);
    }
    element.appendTo($(target));
    // Modify variable name
    if (target === '#var-list') {
      element.click(function(event) {
        $('#varName').val($(this).text());
        $modal_new_var.modal('show');
      });
    }
    return element;
  }

  function _expr_arr_item_receive(item) {
    var label = item.text();
    var name = label.match(/[^\[\]]+/g);
    item.text('');
    if (name && name.length > 1) {
      item.append(name[0]);
      for (var i = 1; i < name.length; i++) {
        var container = $('<ul class="expr-rhs expr-item-list"></ul>');
        newBlock(getType(name[i]), name[i], container);
        item.append('[').append(container).append(']');
      }
    }
    $('.expr-rhs', item).sortable({
      connectWith: '.expr-trash',
      receive: _expr_rhs_receive,
    }).disableSelection();
    item.attr('style', '');
    return item;
  }

  function _expr_lhs_receive(event, ui) {
    var item = $(ui.helper);
    if (item.hasClass('expr-item arr')) {
      _expr_arr_item_receive(item);
    }
    $(this).empty().append(item);
    $('.expr-rhs', item).sortable({
      connectWith: '.expr-trash',
      receive: _expr_rhs_receive,
    }).disableSelection();
  }

  function newExpr(setEventHandler = false) {
    var expr = $('<div class="expr"><ul class="expr-lhs expr-item-list"></ul> <ul class="d-inline-block pl-0"><li class="btn btn-sm">=</li></ul> <ul class="expr-rhs expr-item-list"></ul></div>');

    if (setEventHandler) {
      $('.expr-lhs', expr).sortable({
       receive: _expr_lhs_receive,
      }).disableSelection();

      $('.expr-rhs', expr).sortable({
        connectWith: '.expr-trash',
        receive: _expr_rhs_receive,
      }).disableSelection();
    }
    expr.appendTo('#expr-list');
    return expr;
  }

  function newArrBlock(name, cols, is2d = false, rows = 1) {
    var wrapper = $('<ul class="expr-item-list" data-name="'+name+'" data-rows="'+rows+'" data-cols="'+cols+'" data-is2d="'+is2d+'"></ul>');
    if (!is2d) {
      for (var i = 0; i < cols; i++) {
        newBlock('arr', '['+i+']', wrapper);
      }
    } else {
      for (var i = 0; i < cols; i++) {
        newBlock('arr', '['+0+']['+i+']', wrapper);
      }
      for (var r = 1; r < rows; r++) {
        $('<br>').appendTo(wrapper);
        for (var i = 0; i < cols; i++) {
          newBlock('arr', '['+r+']['+i+']', wrapper);
        }
      }
    }
    wrapper.appendTo($('<li class="arr-wrapper"><span class="btn btn-sm btn-danger">'+name+'</span></li>').appendTo($('#arr-list')));
    $('.expr-item.arr', wrapper).draggable({
      connectToSortable: '.expr-rhs, .expr-lhs',
      revert: "invalid",
      helper: _var_arr_helper,
    });
    return wrapper;
  }

  function _expr_rhs_receive(event, ui) {
    var item = $(ui.helper);
    if (item.hasClass('expr-item arr')) {
      _expr_arr_item_receive(item);
    } else if (item.hasClass('expr-item literal')) {
      $modal_literal_value.data('literal-item', item);
      $('#modal-literal-value').modal('show');
    }
  }

  function _create_literal() {
    var item = $modal_literal_value.data('literal-item');
    var value = $('#literal-value').val().trim();
    if (item.hasClass('str')) {
      value = "'"+value+"'";
    }
    if (value) {
      item.text(value).attr('style', '');
    }
    $modal_literal_value.modal('hide');
  }

  $('#literal-value').on('keypress', function (event) {
    if (event.which === 13) {
      event.preventDefault();
      _create_literal();
    }
  });

  $('#literal-value-ok').click(function(event) {
    _create_literal();
  });

  $modal_literal_value.on('shown.bs.modal', function(event) {
    $('#literal-value').val('').focus();
  });

  $modal_literal_value.on('hide.bs.modal', function(event) {
    var item = $modal_literal_value.data('literal-item');
    if (item.html() === '&nbsp;')
      item.detach();
  });

  $modal_new_array.on('shown.bs.modal', function(event) {
    $modal_new_array.removeClass('was-validated');
    $('#div-arr-rows').addClass('d-none');
    $('table input:text', $modal_new_array).val('0');
    $('#arr-2d').prop('checked', false).change();
    $('#arr-rows').val('1').change();
    $('#arr-cols').change();
    $('#arr-name').val('').focus();
  });

  $('#arr-rows').change(function(event) {
    var arr_rows = parseInt($(this).val());
    if (arr_rows < 1 || arr_rows > 10) {
      arr_rows = arr_rows < 1 ? 1 : 10;
      $(this).val(arr_rows);
    }
    $('#modal-new-array tr:nth-child(n+2):nth-child(-n+'+(arr_rows+1)+')').removeClass('d-none');
    $('#modal-new-array tr:nth-child(n+'+(arr_rows+2)+'):nth-child(-n+11)').addClass('d-none');
  });

  $('#arr-cols').change(function(event) {
    var arr_cols = parseInt($(this).val());
    if (arr_cols < 1 || arr_cols > 10) {
      arr_cols = arr_cols < 1 ? 1 : 10;
      $(this).val(arr_cols);
    }
    $('#modal-new-array tr > :nth-child(n+2):nth-child(-n+'+(arr_cols+1)+')').removeClass('d-none');
    $('#modal-new-array tr > :nth-child(n+'+(arr_cols+2)+'):nth-child(-n+11)').addClass('d-none');
  });

  $('#arr-2d').change(function(event) {
    if ($(this).prop('checked')) {
      $('#div-arr-rows').removeClass('d-none');
      $('#modal-new-array tr th:nth-child(1)').removeClass('d-none');
    } else {
      $('#div-arr-rows').addClass('d-none');
      $('#modal-new-array tr th:nth-child(1)').addClass('d-none');
      $('#arr-rows').val('1').change();
    }
  });

  $('#literal-value-ok').click(function(event) {
    $modal_literal_value.modal('hide');
  });

  function _new_arr_row(items, parent) {
    newBlock('symbol', '[', parent);
    _new_arr_expr_block(items[0], parent);
    for (var i = 1; i < items.length; i++) {
      newBlock('symbol', ',', parent);
      _new_arr_expr_block(items[i], parent);
    }
    newBlock('symbol', ']', parent);
  }

  function _new_arr_expr(name, is2d, data, expr) {
    var expr_lhs = $('.expr-lhs', expr),
        expr_rhs = $('.expr-rhs', expr);

    expr_rhs.removeClass('expr-rhs');
    newBlock('arr', name, expr_lhs);
    if (is2d) {
      newBlock('symbol', '[', expr_rhs);
      $('<br>').appendTo(expr_rhs);
      _new_arr_row(data[0], expr_rhs);
      for (var r = 1; r < data.length; r++) {
        newBlock('symbol', ',', expr_rhs);
        $('<br>').appendTo(expr_rhs);
        _new_arr_row(data[r], expr_rhs);
      }
      $('<br>').appendTo(expr_rhs);
      newBlock('symbol', ']', expr_rhs);
    } else {
      _new_arr_row(data, expr_rhs);
    }
    $('.expr-rhs', expr).sortable({
      connectWith: '.expr-trash',
      receive: _expr_rhs_receive,
    }).disableSelection();
  }

  $('#new-arr-ok').click(function(event) {
    var arr_name = $('#arr-name').val().trim(),
        arr_rows = parseInt($('#arr-rows').val()),
        arr_cols = parseInt($('#arr-cols').val()),
        arr_is2d = $('#arr-2d').prop('checked');

    if (!arr_name.match(/^[_A-Za-z][_A-Za-z0-9]*$/)) {
      $('#modal-new-array').addClass('was-validated');
      return;
    }

    var expr = newExpr();
    var data = [];
    for (var row = 0; row < arr_rows; row++) {
      var row_items = $('input', '#modal-new-array tr:nth-child('+(row+2)+')');
      var arr = [];
      for (var col = 0; col < arr_cols; col++) {
        arr.push($(row_items[col]).val().trim());
      }
      data.push(arr);
    }
    _new_arr_expr(arr_name, arr_is2d, arr_is2d ? data : data[0], expr);
    newArrBlock(arr_name, arr_cols, arr_is2d, arr_rows);
    expr.appendTo('#expr-list');
    $modal_new_array.modal('hide');
    return expr;
  });

  function _var_arr_helper() {
    var name = $(this).parent().data('name');
    if ($(this).hasClass('expr-item arr')) {
      var helper = $(this).clone();
      helper.prepend(name);
      return helper;
    }
    if ($(this).hasClass('expr-item literal'))
      return $(this).clone().html('&nbsp;');
    return $(this).clone();
  }

  $modal_new_var.on('show.bs.modal', function (event) {
    if (event.relatedTarget === undefined) {
      $('#new-var-ok').addClass('d-none');
      $('#edit-var-ok').data('oVar', $('#varName').val()).removeClass('d-none');
      $('#new-var-title').text('修改變數');
    } else {
      $('#varName').val('');
      $('#new-var-ok').removeClass('d-none');
      $('#edit-var-ok').addClass('d-none');
      $('#new-var-title').text('新增變數');
    }
    $('#new-var-form').removeClass('was-validated');
  });

  $modal_new_var.on('shown.bs.modal', function (event) {
    $('#varName').focus();
  });

  function createNewVar() {
    var input = $('#varName').val().trim();
    var form = $('#new-var-form');

    if (!input.match(/^[_A-Za-z][_A-Za-z0-9]*$/)) {
      form.addClass('was-validated');
      return;
    }

    if (input !== "") {
      newBlock('var', input, '#var-list').draggable({
        connectToSortable: '.expr-lhs, .expr-rhs, .expr-trash',
        helper: "clone",
        revert: "invalid",
      });
      $('#varName').val('').focus();
    }
    form.removeClass('was-validated');
  }

  function updateVar() {
    var oVar = $('#edit-var-ok').data('oVar');
    var nVar = $('#varName').val().trim();
    if (!nVar.match(/^[_A-Za-z][_A-Za-z0-9]*$/)) {
      $('#new-var-form').addClass('was-validated');
      return;
    }
    if (oVar !== nVar) {
      $('#var-list .expr-item.var, #expr-list .expr-item.var').each(function(idx, item) {
        if ($(item).text() === oVar)
          $(item).text(nVar);
      });
      }
    $modal_new_var.modal('hide');
  }

  $('#new-var-ok').click(createNewVar);

  $('#edit-var-ok').click(updateVar);

  $('#new-exp').click(function() {
    newExpr(true);
  });

  $('.card-header .expr-item').draggable({
    connectToSortable: '.expr-rhs',
    helper: "clone",
    revert: "invalid",
  });

  $('.expr-trash').sortable({
    receive: function (event, ui) {
      $(ui.item).detach();
      $(ui.helper).detach();
    }
  });

  $('.expr-lhs, .expr-rhs, .expr-list').sortable({
    connectWith: '.expr-trash',
  }).disableSelection();

  $('.expr-arr-list').sortable({
    connectWith: '.expr-trash',
  }).disableSelection();

  //-------------------------------------------------------------------------
  // 初始化先前送出的舊運算式
  function initExprElements(hid = 0) {
    // init vars
    var curr_qid = $('#expr-form input[name="qid"]').val();
    var exprjson;
    try {
      exprjson = exprdata['q'+curr_qid][hid].expr;
    } catch (error) {
      exprjson = {
        'vars': [],
        'arrs': [],
        'exprs': [],
      };
    }
    var items = exprjson['vars'];
    for (id in items) {
      item = items[id];
      newBlock('var', item, '#var-list').draggable({
        connectToSortable: '.expr-rhs, .expr-lhs, .expr-trash',
        revert: "invalid",
        helper: "clone",
      });
    }
    // init arrs
    for (id in exprjson['arrs']) {
      var arr = exprjson['arrs'][id];
      newArrBlock(arr.name, arr.cols, arr.is2d, arr.rows);
    }
    // init expression
    for (id in exprjson['exprs']) {
      var exprstr = exprjson['exprs'][id];
      var tokens = exprstr.match(/('[^']+'|\w+(\[[^\[\]]+\])*|[\(\)+\-*\/]|\[|\]|,)/g);
      if (tokens) {
        if (tokens[1] === '[') {
          var expr = newExpr();
          expr_rhs = exprstr.split(' = ');
          arrdef = expr_rhs[1].match(/\[[^\[\]]*\]/g);
          data = [];
          for (var i = 0; i < arrdef.length; i++) {
            data.push(arrdef[i].match(/[^\[\],]+/g));
          }
          if (tokens[2] === '[')
            _new_arr_expr(tokens[0], true, data, expr);
          else
            _new_arr_expr(tokens[0], false, data[0], expr);
        } else {
          var expr = newExpr(true);
          var expr_rhs = $('.expr-rhs', expr),
              expr_lhs = $('.expr-lhs', expr);

          newBlock(getType(tokens[0]), tokens[0], expr_lhs, true);
          for (var i = 1; i < tokens.length; i++) {
            token = tokens[i];
            newBlock(getType(token), token, expr_rhs, true);
          }
          $('.expr-item>.expr-rhs', expr).sortable({
            connectWith: '.expr-trash',
            receive: _expr_rhs_receive,
          }).disableSelection();
        }
      }
    }
  }

  function genericQSwitch(titleID, titleKey, switchID, formID, curr_qid, qid) {
    $(titleID).text(assignment[titleKey][qid]);
    $($(switchID+' .btn').get(curr_qid)).removeClass('btn-primary').addClass('btn-light');
    $($(switchID+' .btn').get(qid)).removeClass('btn-light').addClass('btn-primary');
    $(formID + ' input[name="qid"]').val(qid+1);
  }

  function generateHistoryItems(items, container, itemContainers, initElementsCallback) {
    try {
      if (items != undefined) {
        for (var i = 0; i < items.length; i++) {
          var item = items[i];
          $('<div class="list-group-item'+(i == 0 ? " active" : "")+'"><span class="badge badge-light">'+(i+1)+'</span> '+(new Date(item.created))+'</div>').appendTo(container);
        }
      }
    } catch(error) {

    }

    $(container).click(function(event) {
      var me = $(event.target);
      if (me.hasClass('active'))
        return;
      $(itemContainers).empty();
      var hid = parseInt($('span', me).text())-1;
      $(container+'>.list-group-item.active').removeClass('active');
      me.addClass('active');
      initElementsCallback(hid);
    });
  }

  function qData_switch(qid) {
    var curr_qid = 0 + $('#expr-form input[name="qid"]').val() - 1;
    if (qid === curr_qid)
      return;
    $('#var-list, #arr-list, #expr-list, #expr-history').empty();
    genericQSwitch('#data-qTitle', 'qData', '#qData-switch', '#expr-form', curr_qid, qid);
    initExprElements();
    generateHistoryItems(exprdata['q'+(qid+1)], '#expr-history', '#var-list, #arr-list, #expr-list', initExprElements);
  }

  function qFlow_switch(qid) {
    var curr_qid = 0 + $('#flow-form input[name="qid"]').val() - 1;
    if (qid === curr_qid)
      return;
    $('#flow-list, #flow-history').empty();
    genericQSwitch('#flow-qTitle', 'qFlow', '#qFlow-switch', '#flow-form', curr_qid, qid);
    initFlowElements();
    generateHistoryItems(flowdata['q'+(qid+1)], '#flow-history', '#flow-list', initFlowElements);
  }

  $('#qData-switch .btn').click(function(event) {
    qData_switch(0 + $(this).text() - 1);
  });

  $('#qFlow-switch .btn').click(function(event) {
    qFlow_switch(0 + $(this).text() - 1);
  });

  qData_switch(0);
  qFlow_switch(0);

  //-------------------------------------------------------------------------
  // 送出答案
  $('#expr-submit').click(function() {
    var data = {
      vars: [],
      arrs: [],
      exprs: [],
    };

    $('.expr-item', '#var-list').each(function(index, obj) {
      data['vars'].push($(obj).text());
    });

    $('.expr-item-list', '#arr-list').each(function(index, obj) {
      var size = $('.expr-item', $(obj)).length;
      data['arrs'].push({name: $(obj).data('name'), cols: $(obj).data('cols'), is2d: $(obj).data('is2d'), rows: $(obj).data('rows')});
    });

    $('.expr', '#expr-list').each(function(index, obj) {
      var tokens = [];
      $('li', $(obj)).each(function(index, item) {
        if ($(item).parent().parent().hasClass('expr') || $(item).parent().parent().parent().hasClass('expr')) {
          tokens.push($(item).text());
        }
      });
      data['exprs'].push(tokens.join(' '));
    });
    $('#jsonstr').val(JSON.stringify(data));
    $('#expr-form').submit();
  });
});

$('#modal-new-array input').addClass('form-control text-center');