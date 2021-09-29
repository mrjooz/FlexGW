(function() {
    function showTopAds(ads) {
        var html = ""
        for (var i = 0; i < ads.length; i++) {
            var ad = ads[i];
            html += "<a target=\"_blank\" href=\"" + decodeURIComponent(ad['url']) + "\">";
            html += "<li>";
            html += '<div class="top-carousel">';
            html += "<div class=\"img-container\" style=\"color:#" + ad['titlecolor'] + ";background:#" + ad['bgcolor'] + " url(" + decodeURIComponent(ad['image']) + ") center right no-repeat\">";
            html += "<div>";
            html += decodeURIComponent(ad['title']);
            html += "</div>";
            html += "<div>";
            html += decodeURIComponent(ad['description']);
            html += "</div>";
            html += '</div>';
            html += '</div>';
            html += "</li>";
            html += "</a>";
        }
        $("#top-ads").html(html);
    }

    function showBottomAds(ads) {
        var html = ""
        for (var i = 0; i < ads.length; i++) {
            var ad = ads[i];
            html += "<a target=\"_blank\" href=\"" + decodeURIComponent(ad['url']) + "\">";
            html += "<li>";
            html += '<div class="news-carousel">';
            html += "<div class=\"img-container\" style=\"color:#" + ad['titlecolor'] + ";background:#" + ad['bgcolor'] + " url(" + decodeURIComponent(ad['image']) + ") center right no-repeat\">";
            html += "<div>";
            html += decodeURIComponent(ad['title']);
            html += "</div>";
            html += "<div>";
            html += decodeURIComponent(ad['description']);
            html += "</div>";
            html += '</div>';
            html += '</div>';
            html += "</li>";
            html += "</a>";
        }
        $("#bottom-ads").html(html);
    }

    function removeAds() {
        $("#top-ads").remove()
        $("#bottom-ads").remove()
    }
    $.ajax({
        url: "/api/ad/top",
        type: "get",
        dataType: "json",
        success: function(res, status, xhr) {
            if (res['ads'].length === 0) {
                $("#top-ads").remove();
            }
            showTopAds(res['ads']);
        },
        error: function(xhr, status, thrown) {
            removeAds();
        }
    });
    $.ajax({
        url: "/api/ad/bottom",
        type: "get",
        dataType: "json",
        success: function(res, status, xhr) {
            if (res['ads'].length === 0) {
                $("#bottom-ads").remove();
            }
            showBottomAds(res['ads']);
        },
        error: function(xhr, status, thrown) {
            removeAds();
        }
    });
})();
