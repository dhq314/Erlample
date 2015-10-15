ErlDocs = function () {
    var search = $("#search"),
        results = $("#results"),
        selected = null,
        resultsCount = 0;

    search.focus(function () {
        if (search.val() == "Module List") {
            search.val("");
        }
    });

    search.keydown(function (e) {
        setTimeout(function () {
            keypress(e);
        }, 0);
    });

    $(window).bind('resize', function () {
        window_resize();
    });
    window_resize();

    var qs = ErlDocs.parse_query(document.location.href);

    if (qs && qs.search) {
        var search_val = decodeURIComponent(qs.search.replace(/\+/g, " "));
        search.val(search_val);
        filter(search_val);
    } else {
        showModules();
    }

    if (qs && qs.i) {
        setSelected(parseInt(qs.i, 10));
    }

    search.focus();

    function setSelected(x, down) {
        down = (typeof down == "undefined") ? false : down;

        if (x >= 0 && x < resultsCount) {
            if (selected != null) {
                results.children("li").eq(selected).removeClass("selected");
            }
            selected = x;
            var selection = results.children("li").eq(x).addClass("selected");
            selection[0].scrollIntoView(down);
        }
    }

    function keypress(e) {
        switch (e.keyCode) {
            case 40:
                setSelected(selected + 1, false);
                break;
            case 38:
                setSelected(selected - 1, false);
                break;
            case 13:
                document.location.href = results.children(".selected").find("a").attr("href");
                break;
            default:
                filter(search.val());
                break;
        }
    }

    function window_resize() {
        //results.height($(window).height() - 60);
        results.height("auto");
    }

    function showModules() {
        var html = [];
        for (var i = 0, count = 0; i < ErlDocs.index_len; i++) {
            var item = ErlDocs.index[i];
            if (item[0] == "mod") {
                var url = WEBURL + "modules/" + item[2] + "/index.html?i=" + i;
                html.push('<li class="', item[0], '"><a href="', url, '"><span class="name">', item[2], '</span><br /><span class="sub">', item[3], '</span></a></li>');
                count++;
            }
        }
        results[0].innerHTML = html.join("");
        resultsCount = count;
        setSelected(0);
    }

    function searchApps(str) {
        var html = [];
        var terms = str.split(" ");
        for (var i = 0, count = 0; i < ErlDocs.index_len; i++) {
            var item = ErlDocs.index[i];
            if (ErlDocs.match(item[2], terms)) {
                var page_name = item[0] == "fun" ? item[4] : "index";
                var url = WEBURL + "modules/" + item[1] + "/" + page_name + ".html?search=" + str + "&i=" + count;
                html.push('<li class="', item[0], '"><a href="', url, '"><span class="name">', item[2], '</span><br /><span class="sub">', item[3], '</span></a></li>');
                if (count++ > 100)
                    break;
            }
        }
        resultsCount = count;
        return html.join("");
    }

    function filter(str) {
        if (str != "") {
            results[0].innerHTML = searchApps(str);
            setSelected(0);
        } else {
            showModules();
        }
    }
};

ErlDocs.match = function (str, terms) {
    for (var i = 0; i < terms.length; i++) {
        if (str.match(new RegExp(terms[i], "i")) == null) {
            return false;
        }
    }
    return true;
};

// This is a nasty check
ErlDocs.is_home = function () {
    return document.title == "Home - erldocs.com (Erlang Documentation)"
        || document.title == "Module Index - erldocs.com (Erlang Documentation)";
};

ErlDocs.parse_query = function (url) {
    var qs = url.split("?")[1];
    if (typeof qs !== "undefined") {
        var arr = qs.split("&"), query = {};
        for (var i = 0; i < arr.length; i++) {
            var tmp = arr[i].split("=");
            query[tmp[0]] = tmp[1];
        }
        return query;
    }
    return false;
};

ErlDocs.get_jsonp = function (data, callbackfun) {
    $.ajax({
        type: "get",
        async: false,
        url: "http://" + ACTURL + "/erlshellaction/",
        dataType: "jsonp",
        jsonp: "callback",
        data: data,
        success: callbackfun
    });
};

ErlDocs.index = index;
ErlDocs.index_len = ErlDocs.index.length;
var mod_list = [];
for (var i = 0; i < ErlDocs.index_len; i++) {
    if (ErlDocs.index[i][0] == "mod") {
        mod_list.push(ErlDocs.index[i][1]);
        ErlDocs.index[i][3] = ErlDocs.index[i][2];
        ErlDocs.index[i][2] = ErlDocs.index[i][1];
    } else if (ErlDocs.index[i][0] == "fun") {
        ErlDocs.index[i][4] = ErlDocs.index[i][2].replace("/", "_");
        ErlDocs.index[i][5] = ErlDocs.index[i][2];
        ErlDocs.index[i][2] = ErlDocs.index[i][1] + ":" + ErlDocs.index[i][2];
    }
}

var docs = new ErlDocs();

$(window).load(function () {

    var ci = 1;
    $('.erlcode').each(function () {
        var eid = "erlcode_" + ci;
        $(this).attr("id", eid);
        var ebid = eid + "_btn";
        var erid = eid + "_ret";
        $(this).append("<div class='erlcode_action'><button action='0' ci='" + ci + "' id='" + ebid + "' type='button'>运行代码</button><span class='erlcode_ret' id='" + erid + "'></span></div>");
        $('#' + eid + ' .container .line').each(function () {
            $(this).attr("contentEditable", "true");
        });
        $('#' + ebid).click(function () {
            if ($(this).attr("action") == 1) {
                return;
            }
            $(this).attr("action", "1");
            $(this).css("background-color", "#EEEEEE");
            $(this).html("处理中...");
            var ci = $(this).attr("ci");
            var erlstr = [];
            $('#erlcode_' + ci + ' .container .line').each(function () {
                erlstr.push($.trim($(this).text()));
            });
            var data = { "action": 5, "erl_str": erlstr.join(" ") };
            ErlDocs.get_jsonp(data, function (rs) {
                var erid = "#erlcode_" + ci + "_ret";
                var erl_ret = rs.result == 1 ? rs.value : "Parse Error!";
                $(erid).html(erl_ret);
                var ebid = "#erlcode_" + ci + "_btn";
                $(ebid).css("background-color", "#FFFFFF");
                $(ebid).html("运行代码");
                $(ebid).attr("action", "0");
            });
        });
        ci++;
    });

    $('.erlcode .syntaxhighlighter').each(function () {
        $(this).attr("title", "代码可编辑");
    });

    if ($('#mod_list_tbody').length > 0) {
        var _html = [],
            mod_count = 0,
            fun_count = [];
        for (i = 0; i < ErlDocs.index_len; i++) {
            var item = ErlDocs.index[i];
            if (item[0] == "mod") {
                mod_count++;
                _html.push("<tr><td>", mod_count, "</td><td><a href='", WEBURL, "modules/", item[2], "/index.html'>", item[2], "</a></td><td>", item[3], "</td><td id='", item[1], "_count'>0</td></tr>");
            }
            if (item[0] == "fun") {
                fun_count[item[1]] ? fun_count[item[1]]++ : fun_count[item[1]] = 1;
            }
        }
        var mlt = $("#mod_list_tbody");
        mlt.html(_html.join(""));
        $("#mod_count").html(mod_count);
        mlt.find("tr").each(function () {
            $(this).hover(
                function () {
                    $(this).css("background-color", "#FAFAD1");
                },
                function () {
                    $(this).css("background-color", "#FFFFFF");
                }
            );
        });
        for (var i in fun_count) {
            $("#" + i + "_count").html(fun_count[i]);
        }
    }
    if ($('#func_list_tbody').length > 0) {

        function func_pages(total, per_page, current) {
            var _html = [];
            var pages = Math.ceil(total / per_page);
            _html.push("<ul>");
            if (pages > 1) {
                if (!current)
                    current = 1;
                var prev = current - 1;
                var next = current + 1;
                var range = 4;
                var showitems = (range * 2) + 1;

                if (current > 2 && current + range + 1 > pages && showitems < pages) {
                    _html.push("<li page='1'>最前</li>");
                }
                if (current > 1 && showitems < pages) {
                    _html.push("<li page='", prev, "'>上一页</li>");
                }

                for (var i = 1; i <= pages; i++) {
                    if (1 != pages && ( !(i >= current + range + 1 || i <= current - range - 1) || pages <= showitems )) {
                        if (current == i) {
                            _html.push("<li class='current'>", i, "</li>");
                        }
                        else {
                            _html.push("<li page='", i, "'>", i, "</li>");
                        }
                    }
                }
                if (current < pages && showitems < pages) {
                    _html.push("<li page='", next, "'>下一页</li>");
                }
                if (current < pages - 1 && current + range - 1 < pages && showitems < pages) {
                    _html.push("<li page='", pages, "'>最后</li>");
                }
            }
            _html.push("</ul>");
            var fg = $("#func_pages");
            fg.html(_html.join(""));
            fg.find("li").each(function () {
                if ($(this).attr("page")) {
                    var page = $(this).attr("page");
                    $(this).click(function () {
                        $("#func_per_page").attr("current", page);
                        draw_func_list();
                    });
                }
            });
        }

        function draw_func_list() {
            var _html = [], func_count = 0;
            var mod = $("#mod_list_sel").val();
            var fpg = $("#func_per_page");
            var per_page = parseInt(fpg.val());
            if (!per_page || per_page < 1) {
                per_page = 20;
            }
            var current = parseInt(fpg.attr("current"));
            if (!current || current < 1) {
                current = 1;
            }
            var start_count = (current - 1) * per_page;
            var end_count = start_count + per_page;
            for (var i = 0; i < ErlDocs.index_len; i++) {
                var item = ErlDocs.index[i];
                if (item[0] == "fun" && ( mod == "" || mod == item[1] )) {
                    func_count++;
                    if (func_count > start_count && func_count <= end_count) {
                        _html.push("<tr><td>", func_count, "</td><td><a href='", WEBURL, "modules/", item[1], "/index.html'>", item[1], "</a></td><td><a href='", WEBURL, "modules/", item[1], "/", item[4], ".html?search=", item[1], ":'>", item[5], "</a></td><td>", item[3], "</td></tr>");
                    }
                }
            }
            var flt = $("#func_list_tbody");
            flt.html(_html.join(""));
            $("#func_count").html(func_count);
            func_pages(func_count, per_page, current);
            fpg.val(per_page);
            flt.find("tr").each(function () {
                $(this).hover(
                    function () {
                        $(this).css("background-color", "#FAFAD1");
                    },
                    function () {
                        $(this).css("background-color", "#FFFFFF");
                    }
                );
            });
        }

        var mod_list_sel = ["<option value=''>全部</option>"],
            mod_list_sel_len = mod_list.length;
        for (i = 0; i < mod_list_sel_len; i++) {
            mod_list_sel.push("<option value='", mod_list[i], "'>", mod_list[i], "</option>");
        }
        var mls = $('#mod_list_sel');
        mls.html(mod_list_sel.join(""));
        mls.change(function () {
            $("#func_per_page").attr("current", 1);
            draw_func_list()
        });
        draw_func_list();
    }

    $("#casual_look").click(function () {
        var index_len = index.length,
            arr = [];
        for (var i = 0; i < index_len; i++) {
            if (index[i][0] == "fun") {
                arr.push(index[i]);
            }
        }
        var item = arr[Math.floor(Math.random() * arr.length)];
        var func_arr = item[2].split(":");
        var func_name = func_arr[1].replace("/", "_");
        var url = WEBURL + "modules/" + item[1] + "/" + func_name + ".html?search=" + item[1] + ":";
        window.location = url;
    });

});

ErlDocs.is_phone = function() {
    navigator.userAgent.match(/(iPhone|iPod|Android|ios)/i);
};