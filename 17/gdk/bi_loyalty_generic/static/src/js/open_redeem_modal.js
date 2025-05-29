$(document).ready(function () {
    var i = 0
    if ($("div#redeem_modal").length == 2) {
        $("div#redeem_modal").each(function () {
            i += 1
            if (i == 1) {
                $(this).remove()
            }
        })
    }


});