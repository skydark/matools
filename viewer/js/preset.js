(function(){
// alasql 的 localstorage db 目前有很多问题，故先自己实现
var toJSON = JSON.stringify;
var fromJSON = JSON.parse;
var preset = [];

if(window.localStorage){
  if (!window.localStorage.preset) {
    window.localStorage.preset = toJSON([{
      name: "按稀有度降序",
      query: "order by rarity desc"
    }, {
      name: "Vilor的作品",
      query: 'where illustrator="Vilor"'
    }, {
      name: "珂莱姆",
      query: 'where name like "%珂莱姆"'
    }, {
      name: "cost至少40的剑城卡",
      query: 'where cost >= 40 and country_id=1 order by rarity desc'
    }, {
      name: "义妹期",
      query: 'where card_version=223'
    }]);
  }
  try {
    preset = fromJSON(window.localStorage.preset);
  } catch(err) {
    console.log(err);
    preset = [];
  }
}else{
  alert('浏览器不支持本地存储，无法使用预设功能！');
  $('#preset-query-dropdown').remove();
}

var commit_preset = function() {
  window.localStorage.preset = toJSON(preset);
};

var refresh_presets = function () {
  $("#preset-query-menu>li.preset-set-query-li").remove();
  for (var i=0; i<preset.length; i++) {
    var name = preset[i]['name'];
    var query = preset[i]['query'];
    //console.log(name);console.log(query);
    var $close = $('<button type="button" class="close preset-delete">&times;</button>').data("query_id", i).click(function(e) {
      preset.splice($(this).data('query_id'), 1);
      commit_preset();
      refresh_presets();
    });
    $('<li>').addClass("preset-set-query-li")
      .append($('<a>').addClass("preset-set-query").text(name)
        .data("query", query).append($close)
        .click(function(e) {
          $('#query').val($(this).data('query'));
          $('#form-query').submit();
        }))
      .appendTo($("#preset-query-menu"));
  }
};
$('#preset-add').on('show.bs.modal', function(e) {
  $('#preset-name').val("新的预设");
  $('#preset-query').val($('#query').val());
});
$('#preset-submit').click(function(e) {
  $('#preset-add').modal('hide');
  preset.push({
    'name':$('#preset-name').val(),
    'query':$('#preset-query').val()
  });
  commit_preset();
  refresh_presets();
});

refresh_presets();
})();