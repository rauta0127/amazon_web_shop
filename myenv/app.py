from flask import Flask, render_template, url_for, request, redirect
from flask_cors import CORS
import review_stealth_checker
import json
import threading
import pandas as pd

app = Flask(__name__)
CORS(app)

# Values
percent = totalReviewCount = totalReviewRating = meter5Star = meter4Star = meter3Star = meter2Star = meter1Star = 0
stealth_percentage = high_probability_stealth_reviwer_count = low_probabilty_stealth_reviewer_count = wrong_data_reviewer_count = 0
high_probability_stealth_reviewers = low_probability_stealth_reviewers = wrong_data_reviewers = []
item_title = ''
status = 'URL Waiting..'


def reviewStealthCheck(item_url):
    review_stealth_checker.main(item_url)

@app.route('/', methods=['GET', 'POST'])
def index():
    percent = totalReviewCount = totalReviewRating = meter5Star = meter4Star = meter3Star = meter2Star = meter1Star = 0
    stealth_percentage = high_probability_stealth_reviwer_count = low_probabilty_stealth_reviewer_count = wrong_data_reviewer_count = 0
    high_probability_stealth_reviewers = low_probability_stealth_reviewers = wrong_data_reviewers = []
    item_title = ''
    status = 'URL Waiting..'
    return render_template("index.html")

@app.route('/scrape', methods=['GET', 'POST'])
def scrape():
    item_url = request.form['item_url']
    t = threading.Thread(target=reviewStealthCheck, args=(item_url, ))
    t.start()
    return redirect(url_for('index'))

@app.route("/progress", methods=['GET', 'POST'])
def progress():
    print ('Main Progress: {}'.format(review_stealth_checker.percent))
    #percent = int(request.form['percent'])
    response_json = {'percent': review_stealth_checker.percent,
                        'status': review_stealth_checker.status,

                        'item_title': review_stealth_checker.item_title,
                        'totalReviewCount': review_stealth_checker.totalReviewCount,
                        'totalReviewRating': review_stealth_checker.totalReviewRating,
                        'star': {
                                    'meter5Star': review_stealth_checker.meter5Star,
                                    'meter4Star': review_stealth_checker.meter4Star,
                                    'meter3Star': review_stealth_checker.meter3Star,
                                    'meter2Star': review_stealth_checker.meter2Star,
                                    'meter1Star': review_stealth_checker.meter1Star
                                },
                        'stealth_stats': {
                                            'stealth_percentage': review_stealth_checker.stealth_percentage,
                                            'high_probability_stealth_reviwer_count': review_stealth_checker.high_probability_stealth_reviwer_count,
                                            'low_probabilty_stealth_reviewer_count': review_stealth_checker.low_probabilty_stealth_reviewer_count,
                                            'wrong_data_reviewer_count': review_stealth_checker.wrong_data_reviewer_count,
                        },
                        'high_probability_stealth_reviewers': {},
                        'low_probability_stealth_reviewers': {},
                        'wrong_data_reviewers': {},
                    }

    if len(review_stealth_checker.high_probability_stealth_reviewers) > 0:
        for i, reviewer in enumerate(review_stealth_checker.high_probability_stealth_reviewers):
            name = reviewer['name']
            score = reviewer['score']
            reviewed_at = reviewer['reviewed_at']
            url = reviewer['url']
            helpful_votes = reviewer['helpful_votes']
            reviews = reviewer['reviews']
            reviewer_ranking = reviewer['reviewer_ranking']
            each_json = {'name': name, 'score': score, 'reviewed_at': reviewed_at, 
                            'url': url, 'helpful_votes': helpful_votes, 'reviews': reviews, 'reviewer_ranking': reviewer_ranking}
            response_json['high_probability_stealth_reviewers'][i] = each_json

    if len(review_stealth_checker.low_probability_stealth_reviewers) > 0:
        for i, reviewer in enumerate(review_stealth_checker.low_probability_stealth_reviewers):
            name = reviewer['name']
            score = reviewer['score']
            reviewed_at = reviewer['reviewed_at']
            url = reviewer['url']
            helpful_votes = reviewer['helpful_votes']
            reviews = reviewer['reviews']
            reviewer_ranking = reviewer['reviewer_ranking']
            each_json = {'name': name, 'score': score, 'reviewed_at': reviewed_at, 
                            'url': url, 'helpful_votes': helpful_votes, 'reviews': reviews, 'reviewer_ranking': reviewer_ranking}
            response_json['low_probability_stealth_reviewers'][i] = each_json

    if len(review_stealth_checker.wrong_data_reviewers) > 0:
        for i, reviewer in enumerate(review_stealth_checker.wrong_data_reviewers):
            name = reviewer['name']
            score = reviewer['score']
            reviewed_at = reviewer['reviewed_at']
            url = reviewer['url']
            helpful_votes = reviewer['helpful_votes']
            reviews = reviewer['reviews']
            reviewer_ranking = reviewer['reviewer_ranking']
            each_json = {'name': name, 'score': score, 'reviewed_at': reviewed_at, 
                            'url': url, 'helpful_votes': helpful_votes, 'reviews': reviews, 'reviewer_ranking': reviewer_ranking}
            response_json['wrong_data_reviewers'][i] = each_json


    print (response_json)
    return json.dumps(response_json)

if __name__ == '__main__':
    app.run(debug=True)