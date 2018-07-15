var progressStIntr;

function progress() {
    var hostUrl= 'http://localhost:5000/progress';
    $.ajax({
        url: hostUrl,
        type:'POST',
        dataType: 'json',
        headers: {
            'Content-Type': 'application/json'
        },
        success: function(data) {
            $('.progress-bar').css('width', data['percent']+'%').attr('aria-valuenow', data['percent']);
            $('.progress-bar-label').text(data['percent']+'%');

            $('#status').text(data['status']);

            $('#item_title').text(data['item_title']);

            $('#totalReviewCount').text(data['totalReviewCount']);
            $('#totalReviewRating').text(data['totalReviewRating']);
            $('#meter5Star').text(data['star']['meter5Star']+'%');
            $('#meter4Star').text(data['star']['meter4Star']+'%');
            $('#meter3Star').text(data['star']['meter3Star']+'%');
            $('#meter2Star').text(data['star']['meter2Star']+'%');
            $('#meter1Star').text(data['star']['meter1Star']+'%');

            $('#stealth_percentage').text(data['stealth_stats']['stealth_percentage']+'%');
            $('#high_probability_stealth_reviwer_count').text(data['stealth_stats']['high_probability_stealth_reviwer_count']);
            $('#low_probabilty_stealth_reviewer_count').text(data['stealth_stats']['low_probabilty_stealth_reviewer_count']);
            $('#wrong_data_reviewer_count').text(data['stealth_stats']['wrong_data_reviewer_count']);

            if (Object.keys(data['high_probability_stealth_reviewers']).length != 0) {
                var h = "<div>*** high_probability_stealth_reviewers ***</div>";
                $('#high_probability_stealth_reviwers').append(h);
                for (var i in data['high_probability_stealth_reviewers']) {
                    var h = "<div>----------------</div>"
                            + "<div>name: "
                            + data['high_probability_stealth_reviewers'][i]['name']
                            + "</div>"
                            + "<div>score: "
                            + data['high_probability_stealth_reviewers'][i]['score']
                            + "</div>"
                            + "<div>reviewed_at: "
                            + data['high_probability_stealth_reviewers'][i]['reviewed_at']
                            + "</div>"
                            + "<div>url: "
                            + data['high_probability_stealth_reviewers'][i]['url']
                            + "</div>"
                            + "<div>helpful_votes: "
                            + data['high_probability_stealth_reviewers'][i]['helpful_votes']
                            + "</div>"
                            + "<div>reviews: "
                            + data['high_probability_stealth_reviewers'][i]['reviews']
                            + "</div>"
                            + "<div>reviewer_ranking: "
                            + data['high_probability_stealth_reviewers'][i]['reviewer_ranking']
                            + "</div>";
                    $('#high_probability_stealth_reviwers').append(h);
                };
                var h = "<div>=========================</div>";
                $('#high_probability_stealth_reviwers').append(h);
            };

            if (Object.keys(data['low_probability_stealth_reviewers']).length != 0) {
                var h = "<div>*** low_probability_stealth_reviewers ***</div>";
                $('#low_probability_stealth_reviewers').append(h);
                for (var i in data['low_probability_stealth_reviewers']) {
                    var h = "<div>----------------</div>" 
                            + "<div>name: "
                            + data['low_probability_stealth_reviewers'][i]['name']
                            + "</div>"
                            + "<div>score: "
                            + data['low_probability_stealth_reviewers'][i]['score']
                            + "</div>"
                            + "<div>reviewed_at: "
                            + data['low_probability_stealth_reviewers'][i]['reviewed_at']
                            + "</div>"
                            + "<div>url: "
                            + data['low_probability_stealth_reviewers'][i]['url']
                            + "</div>"
                            + "<div>helpful_votes: "
                            + data['low_probability_stealth_reviewers'][i]['helpful_votes']
                            + "</div>"
                            + "<div>reviews: "
                            + data['low_probability_stealth_reviewers'][i]['reviews']
                            + "</div>"
                            + "<div>reviewer_ranking: "
                            + data['low_probability_stealth_reviewers'][i]['reviewer_ranking']
                            + "</div>";
                    $('#low_probability_stealth_reviewers').append(h);
                };
                var h = "<div>=========================</div>";
                $('#low_probability_stealth_reviewers').append(h);
            };

            if (Object.keys(data['wrong_data_reviewers']).length != 0) {
                var h = "<div>*** wrong_data_reviewers ***</div>";
                $('#wrong_data_reviewers').append(h);
                for (var i in data['wrong_data_reviewers']) {
                    var h = "<div>----------------</div>" 
                            + "<div>name: "
                            + data['wrong_data_reviewers'][i]['name']
                            + "</div>"
                            + "<div>score: "
                            + data['wrong_data_reviewers'][i]['score']
                            + "</div>"
                            + "<div>reviewed_at: "
                            + data['wrong_data_reviewers'][i]['reviewed_at']
                            + "</div>"
                            + "<div>url: "
                            + data['wrong_data_reviewers'][i]['url']
                            + "</div>"
                            + "<div>helpful_votes: "
                            + data['wrong_data_reviewers'][i]['helpful_votes']
                            + "</div>"
                            + "<div>reviews: "
                            + data['wrong_data_reviewers'][i]['reviews']
                            + "</div>"
                            + "<div>reviewer_ranking: "
                            + data['wrong_data_reviewers'][i]['reviewer_ranking']
                            + "</div>";
                    $('#wrong_data_reviewers').append(h);
                };
                var h = "<div>=========================</div>";
                $('#wrong_data_reviewers').append(h);
            };
            


            if(data['percent'] == 100){
                clearInterval(progressStIntr)
                //alert("Convert Complete");
                document.getElementById("progress-bar-label").innerText = "Complete!";
                $(".progress-bar").removeClass('active');
                document.getElementById("progress-bar-label").innerText = "Complete!";
            }

        },
        error: function(XMLHttpRequest, textStatus, errorThrown) {
            alert("error");
        },   
    });
}

function progressCheck(time){
    progressStIntr = setInterval('progress()', time);
}

$('#submit').on('click', function() {
    alert("Start");
});

progressCheck(1000)

function progressCheck(time){
    progressStIntr = setInterval('progress()', time);
}