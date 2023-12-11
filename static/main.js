import { $ } from "/static/jquery/src/jquery.js";

//  This imports the $ function from the jQuery library. 
//  In jQuery the $ function is used to wrap HTML nodes with jQuery features.
// export function say_hi() {
//     console.log("Hello");
// }

export function say_hi(elt) {
    console.log("Say hi to", elt);
}

export function make_table_sortable($table) {

    $(document).ready(function() {
        $("table th").on("click", function(e) {

            if($(this).hasClass("sortable")){

                // console.log(column.index())
                // const column = $(e).index();
                const column = $(this).index();
                //  If it's unsorted or sorted descending, make it instead sorted ascending. 
                //  If it's sorted ascending, make it sorted descending.
                //  sort-asc, sort-desc
                
                // const tr_array = $table.find("tbody > tr > td:last-child").css("color", "red").map(function(){
                //     return parseFloat($(this).text());
                // }).toArray()

                // const tr_array = $table.find("tbody > tr > td:last-child").css("color", "red").toArray()
                var sortdir = 0;
                
                //  return tr's array
                var rec = $('table').find('tbody>tr').get()
                console.log($table)
                //  case th.class has sort-asc => descending
                if ($table.hasClass("sort-asc")){
                    $table.addClass("sort-desc");
                    $table.removeClass("sort-asc");

                    $table.find('th').eq(column).addClass('sort-desc');
                    $table.find('th').eq(column).removeClass("sort-asc");

                    sortdir=-1;
                }else if($table.hasClass("sort-desc")){
                // case th.class is unsorted or sort-desc => sort-asc
                // Calling removeClass with no parameters will remove all of the item's classes.
                    $table.removeClass("sort-desc")
                    $table.addClass("unsorted")

                    $table.find('th').eq(column).addClass('sort-asc');
                    $table.find('th').eq(column).removeClass('sort-desc');
                }else{
                    // if it's unsorted => ascending
                    $table.removeClass("unsorted")
                    $table.addClass("sort-asc")
                    $table.find('th').eq(column).addClass('sort-asc');
                    $table.find('th').eq(column).removeClass('unsorted');
                    sortdir=1;
                    // add initial index for unstored

                    // if($(rec).attr("data-index")){
                        
                    // }
                    $.each(rec, function(index, row){
                        // row = tr
                        $(row).attr("data-index", index)
                    })

                }            

                rec.sort(function (a, b) {

                    if($table.hasClass("unsorted")){
                        var val1 = parseFloat($(a).data("index"))
                        var val2 = parseFloat($(b).data("index"))
                        if(val1 > val2){
                            return 1;
                        }else if(val1 < val2){
                            return -1;
                        }else{
                            return 0;
                        }
                    }else{  

                        // var val1 = parseFloat($(a).children('td').eq(column).text())
                        // var val2 = parseFloat($(b).children('td').eq(column).text())
                        // console.log($(a).children('td').eq(column).data("value"));
                        console.log($(a).children('td').eq(column));

                        // if($(a).children('td').eq(column))
                        try{
                            //  working
                            // console.log("weight");
                            // console.log($(a).children('td').eq(column).data("weight"));

                            if($(a).children('td').eq(column).hasClass("profile")){
                                // I dont like it
                                try{
                                    var val1 = eval($(a).children('td').eq(column).data("value").slice(0, -1))
                                    var val2 = eval($(b).children('td').eq(column).data("value").slice(0, -1))
                                }catch{
                                    var val1 = NaN
                                    var val2 = NaN
                                }
                            }else{
                                var val1 = eval($(a).children('td').eq(column).data("value"))
                                var val2 = eval($(b).children('td').eq(column).data("value"))
                            }
                            return (val1 < val2)?-sortdir:(val1>val2)?sortdir:0;
                        }catch{
                            console.log("it's input box");
                        }
                    }
                });

                //https://stackoverflow.com/questions/17905646/how-to-add-attribute-with-value-in-td-tag-with-jquery
                $.each(rec, function(index, row) {
                    $('table > tbody').append(row);
                });


                //  select last cell
                // let $tbody = $table.find("tbody > tr > td:last-child").css("color", "red")
                // https://stackoverflow.com/questions/16570564/jquery-get-an-array-of-text
                
            }
        });
    });
}

export function make_form_async($form) {

    $("form").on("submit", (e) => {
        console.log(e.target)
        const form_data = new FormData($(e.target).get(0));
        $(e.target).find("input").attr("disabled", "");

        /*
            The URL of the submit view as url
            The FormData object as data
            POST as the type
        */
            console.log(e.target.action)
            $.ajax(e.target.action, {
                url: e.target.action,
                type: "POST",
                data: form_data,
                processData: false,
                contentType: false,
                mimeType: "enctype",
                success: () => {
                    console.log("Upload succeeded");
                },
                error: () => {
                    console.log("error");
                },
                complete: () => {
                    $(e.target).find("input").attr("disabled", false);
                }
                
            })
    e.preventDefault();
    })
}

export function make_grade_hypothesized ($table) {
    $(document).ready(function() {
        var button = $("<button>").text("Hypothesize").css({ width: "100px" });
        $("table").before(button);

        button.on("click", function(e) {

            //  when current is hypo => change to actual
            if($("table").hasClass("hypothesized")){
                $("table").removeClass("hypothesized");
                $("table").addClass("Actualgrades");
                button.text("Hypothesize");

                var temp = $("table").find("tbody > tr > input ");
                $.each(temp, function(index, input){
                    var temp = $(input).data("origin");

                    var origin_td = $('<td class="alnright profile"></td>');
                    origin_td.text(temp);
                    $(origin_td).data("value",temp);
                    $(input).replaceWith(origin_td);
                })
                var tfoot = $("table").find("tfoot > tr > th");

                tfoot.eq(1).text(tfoot.eq(0).data("origin") + "%");
            }else{  //  when current is actual || None => hypo
                $("table").removeClass("Actualgrades");
                $("table").addClass("hypothesized");      
                button.text("Actual grades");

                var temp = $("table").find("tbody > tr > td");

                $.each(temp, function(index, td){
                    var data_value = $(td).data("value");
                    var data_weight = $(td).data("weight");

                    // console.log(data_value);
                    if(data_value == "Missing" || data_value == "Ungraded" || data_value == "Not"){
                        var input = $('<input type="number" />').css({width: "60px" , "margin-left": "530px"}).addClass("alnright");
                        $(input).data("origin", data_value);
                        $(input).addClass("profile");

                        $(input).data("weight",data_weight);
                        // $(td).replaceWith(input);
                        // console.log(td)
                        $(td).replaceWith(input);
                    }else{
                        $(td).data("weight", data_weight);
                    }
                })
                compute(temp)
            }
        })
        


    });
}

export function compute($td){
    $(document).ready(function() {

        var $tr = $td.closest('tr');
        $("tr").on("change", function(e){
            var total_sum = 0;
            var total_weight = 0;
            var final = 0;
            console.log("changed");
            // console.log($td);
            $.each($tr, function(index,row){
                // console.log(row);
                var weight = parseFloat($(row).find('td:first-child').data("weight"));
                
                // var weight = parseFloat($(row).find('td:last-child, input:last-child').data("weight"));
                var last_child = $(row).find('td:last-child, input:last-child');
                
                console.log(weight)
                // console.log(weight);
                // console.log(lastChildInRow);
                if(last_child.is('td')){
                    // console.log(last_child.data("value").slice(0, -1), " is added");
                    total_sum += parseFloat(last_child.data("value").slice(0, -1)) / 100 * weight;
                    // console.log("total sum = ", total_sum);
                    total_weight += weight
                }else{
                    console.log("input");
                    if($(last_child).val()){
                        total_sum += parseFloat($(last_child).val()) / 100 * weight;
                        // console.log("total sum = ", total_sum);
                        total_weight += weight
                    }else{
                        //  nothing
                    }
                }
                
            })//    end each
            //  need to initialize total sum after calculate
            console.log("total sum = ", total_sum , " total weight =", total_weight);
            var final = (total_sum / total_weight * 100 ).toFixed(1);
            console.log("final = ", final);
            var tfoot = $("tr").closest("table").find("tfoot > tr> th:last-child").text(final + "%");
            console.log(tfoot)
        })
})
}