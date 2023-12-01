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

}


say_hi($("h1"));
