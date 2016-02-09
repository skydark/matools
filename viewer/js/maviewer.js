(function(){
var DEFAULT_PAGESIZE = 30;
var state = {
    db: null,
    pagenum: 1,
    pagesize: 1,
    results: []
};

state.db = MA_DB;
/*
var MA_DB = "./ma.json";
$.getJSON(MA_DB, function(json) {
    state.db = json;
    $('#form-query').submit();
}).fail(function(d, status, error) {
    console.log("数据库加载失败, status: " + status + ", error: " + error);
});
*/

var _do_query = function(query) {
    try {
        return alasql('SELECT * FROM ? ' + query, [state.db]);
    } catch (err) {
        alert("执行查询时发生错误："+err);
    }
    return null;
};
var _do_query_by_id = function(id) {
    try {
        return alasql('SELECT * FROM ? WHERE master_card_id = ?', [state.db, id])[0];
    } catch (err) {
        alert("执行查询时发生错误："+err);
    }
    return null;
};

/* // PyQt
var _do_query = function(query) {$.parseJSON(pyobj.query(query));};
var _do_query_by_id = function(id) {$.parseJSON(pyobj.query_by_id(id));};
*/

$(".number-only").keydown(function (e) {
    // Allow: backspace, delete, tab, escape, enter and .
    if ($.inArray(e.keyCode, [46, 8, 9, 27, 13, 110, 190]) !== -1 ||
         // Allow: Ctrl+A, Command+A
        (e.keyCode == 65 && ( e.ctrlKey === true || e.metaKey === true ) ) || 
         // Allow: home, end, left, right, down, up
        (e.keyCode >= 35 && e.keyCode <= 40)) {
             // let it happen, don't do anything
             return;
    }
    // Ensure that it is a number and stop the keypress
    if ((e.shiftKey || (e.keyCode < 48 || e.keyCode > 57)) && (e.keyCode < 96 || e.keyCode > 105)) {
        e.preventDefault();
    }
});

$(".section-detail").hide();

var get_total_page = function() {
    return Math.max(1, Math.floor((state.results.length-1)/state.pagesize)+1);
};

var reload = function() {
    var pagesize = parseInt($('#pagesize').val(), 10);
    pagesize = Math.max(isNaN(pagesize)? DEFAULT_PAGESIZE : pagesize, 1);
    state.pagesize = pagesize;
    var pagenum = parseInt($('#pagenum').val(), 10);
    pagenum = Math.max(isNaN(pagenum)?1:pagenum, 1);
    pagenum = Math.min(pagenum, get_total_page());
    state.pagenum = Math.max(pagenum, 1);
};
var refresh = function() {
    var pagesize = state.pagesize;
    $('#pagesize').val(pagesize);
    var pagenum = state.pagenum;
    $('#pagenum').val(pagenum);
    $('#total-page').text(get_total_page());
    var $list = $('#result-list');
    $list.empty();
    var results = state.results;
    for (var i = (pagenum-1)*pagesize; i < pagenum*pagesize; i++) {
        if (i >= results.length) break;
        var result = results[i];
        $('<li>').addClass("list-group-item")
            .append($('<img src="image/face/face_'+result['character_id']+'.png">').addClass('result-face'))
            .append($('<div class="result-name">'+result['name']+'</div>'))
            .data("card-id", result['master_card_id']).click(function(e) {
                show_detail($(this).data("card-id"));
            })
            .appendTo($list);
    }
};

var do_query = function(query) {
    results = _do_query(query);
    if (!results) return;
    $('#query').val(query);
    state.results = results;
    // $('#pagenum').val(1);
    $(".section-detail").hide();
    $(".section-query").show();
    reload();
    refresh();
};

var show_detail = function(id) {
    var details = _do_query_by_id(id);
    if (!details) return;
    $('#detail-name').text(details.name);
    $('#detail-face').attr('src', 'image/face/face_'+details.character_id+'.png');
    $('#detail-rarity').text(details.rarity).click(function(e) {
        do_query('where rarity='+details.rarity+' order by rarity desc');
    });
    $('#detail-sex').text(details.distinction==1?"男":"女").click(function(e) {
        do_query('where distinction='+details.distinction);
    });
    var countrys = ["剑术之城", "技巧之场", "魔法之派", "妖精"];
    $('#detail-country').text(countrys[details.country_id-1]).click(function(e) {
        do_query('where country_id='+details.country_id);
    });
    $('#detail-attack-type').text(countrys[details.attack_type-1]).click(function(e) {
        do_query('where attack_type='+details.attack_type);
    });
    $('#detail-cost').text(details.cost).click(function(e) {
        do_query('where cost='+details.cost);
    });
    $('#detail-illustrator').text(details.illustrator).click(function(e) {
        do_query('where illustrator="'+details.illustrator+'"');
    });
    $('#detail-grow').text(details.grow_name + '; ' + details.growth_rate_text);
    $('#detail-skill-name').text(details.skill_name);
    $('#detail-skill-kana').text(details.skill_kana);
    $('#detail-skill-desc').text(details.skill_description);
    // $('#detail-sell').text(details.sale_price);
    $('#detail-card-version').text(details.card_version).click(function(e) {
        do_query('where card_version='+details.card_version);
    });
    $('#detail-desc').text(details.char_description);
    var postfixes = [
      details.image1_id+'.png',
      details.image1_id+'_horo.png',
      details.image2_id+'.png',
      details.image2_id+'_horo.png'
    ];
    $('.detail-image').each(function(i, elm) {
      var postfix = postfixes[i];
      this.src = 'image/full_cards/full_thumbnail_chara_' + postfix;
      this.onerror = function() {
        this.onerror = null;
        this.src = 'image/card/thumbnail_chara_' + postfix;
      };
    });
    $(".section-query").hide();
    $(".section-detail").show();
};

$('#btn-hide-detail').click(function(e) {
    $(".section-detail").hide();
    $(".section-query").show();
});
$('#tab-detail a').click(function (e) {
    e.preventDefault();
    $(this).tab('show');
});

$('#btn-first').click(function(e) {
    state.pagenum = 1;
    refresh();
});
$('#btn-last').click(function(e) {
    state.pagenum = get_total_page();
    refresh();
});
$('#btn-next').click(function(e){
    if (state.pagenum < get_total_page()) {
        state.pagenum += 1;
        refresh();
    }
});

$('#btn-prev').click(function(e){
    if (state.pagenum > 1) {
        state.pagenum -= 1;
        refresh();
    }
});

$('#form-query').submit(function(e){
    e.preventDefault();
    var query = $('#query').val();
    do_query(query);
});

$('#form-query').submit();
})();
