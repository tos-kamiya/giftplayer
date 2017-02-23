$(document).ready(function() {{
  $("select.match{quiz_num}").change(function () {{
    var vals = [];
    $("select.match{quiz_num}").each(function () {{
      vals.push($(this).val());
    }});
    var sorted_vals = vals.slice().sort();
    var duplicated_vals = [];
    for (var i = 0; i < sorted_vals.length - 1; ++i) {{
      var svi = sorted_vals[i];
      if (svi !== "" && sorted_vals[i + 1] === svi)
        duplicated_vals.push(svi);
    }}
    var str = "";
    $("[name=quiz{quiz_num}_right1] option").each(function () {{
      if (duplicated_vals.indexOf($(this).val()) != -1)
        str += 'error: "' + $(this).text() + '" is selected twice (or more). ';
    }});
    $("div.match{quiz_num}").text(str);
}}).change();
}});
