# -*- coding: utf-8 -*-
"""
@author: rauta0127
@brief: This script checks amazon shop item review stealth probability 
"""
import pandas as pd
import requests
from bs4 import BeautifulSoup
import lxml
import sys
import subprocess as sbp
import datetime as dt
from selenium import webdriver
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support import expected_conditions as ec
from selenium.webdriver.common.desired_capabilities import DesiredCapabilities
from selenium.webdriver.common.by import By
import urllib
import traceback
from tqdm import tqdm
import logging

global percent, item_title, totalReviewCount, totalReviewRating, meter5Star, meter4Star, meter3Star, meter2Star, meter1Star, df
global stealth_percentage, high_probability_stealth_reviwer_count, low_probabilty_stealth_reviewer_count, wrong_data_reviewer_count
global high_probability_stealth_reviewers, low_probability_stealth_reviewers, wrong_data_reviewers
global status
percent = totalReviewCount = totalReviewRating = meter5Star = meter4Star = meter3Star = meter2Star = meter1Star = 0
stealth_percentage = high_probability_stealth_reviwer_count = low_probabilty_stealth_reviewer_count = wrong_data_reviewer_count = 0
high_probability_stealth_reviewers = low_probability_stealth_reviewers = wrong_data_reviewers = []
item_title = ''
status = 'URL Waiting..'
df = pd.DataFrame()

def transformStarCount(text):
    #----------------------
    # Japanese: "5つ星のうち4.0" => 4.0
    # English: "3.0 out of 5 stars" => 3.0
    #----------------------
    if 'のうち' in text:
        star_count = float(text.split('のうち')[1])
    elif 'out of' in text:
        star_count = float(text.split(' out of ')[0])
    return star_count

def transformDateTimestamp(text):
    #----------------------
    # Japanese: "2017年12月30日" => datetime.datetime(2017, 12, 30, 0, 0)
    # English: "on June 7, 2015" => datetime.datetime(2015, 6, 7, 0, 0)
    #----------------------
    try:
        if '年' in text:
            timestamp = dt.datetime.strptime(text, "%Y年%m月%d日")
        elif 'on' in text:
            timestamp = dt.datetime.strptime(text, "on %B %d, %Y")
    except:
        print ('transforming datetime strptime wrong..')
        pass
    return timestamp

def encodingURL(url):
    #----------------------
    # "https://www.amazon.co.jp/パワープロダクション-エキストラ
    # -アミノアシッドプロテイン-サワーミルク味-560g/dp/B0798B2YK2
    # /ref=cm_cr_arp_d_product_sims"
    # =>
    # "https://www.amazon.co.jp/%E3%83%91%E3%83%AF%E3%83%BC
    # %E3%83%97%E3%83%AD%E3%83%80%E3%82%AF%E3%82%B7%E3%83%A7%E3
    # %83%B3-%E3%82%A8%E3%82%AD%E3%82%B9%E3%83%88%E3%83%A9-%E3%82
    # %A2%E3%83%9F%E3%83%8E%E3%82%A2%E3%82%B7%E3%83%83%E3%83%89%E3
    # %83%97%E3%83%AD%E3%83%86%E3%82%A4%E3%83%B3-%E3%82%B5%E3%83%AF
    # %E3%83%BC%E3%83%9F%E3%83%AB%E3%82%AF%E5%91%B3-560g/dp/B0798B2YK2
    # /ref%3Dcm_cr_arp_d_product_sims
    #----------------------
    url = urllib.parse.quote(url, safe='/:')
    return url

def calcSpyProbability(helpful_votes, reviews):
    probability = 0
    if helpful_votes == 1 and reviews == 1:
        probability = 1
    elif helpful_votes == 0 and reviews == 1:
        probability = 1
    elif reviews > 0:
        if helpful_votes/reviews < 0.3:
            probability = 0.5
    return probability

#-------------------------- Main --------------------------
def main(item_url):
    global percent, item_title, totalReviewCount, totalReviewRating, meter5Star, meter4Star, meter3Star, meter2Star, meter1Star
    global stealth_percentage, high_probability_stealth_reviwer_count, low_probabilty_stealth_reviewer_count, wrong_data_reviewer_count
    global high_probability_stealth_reviewers, low_probability_stealth_reviewers, wrong_data_reviewers
    global status

    log_fmt = '%(asctime)s- %(name)s - %(levelname)s : %(message)s'
    logging.basicConfig(filename='logging.log', filemode='w', format=log_fmt)
    root_logger = logging.getLogger('')
    root_logger.setLevel(logging.INFO)

    #item_url = input('Please input item amazon url: ')
    
    if not 'https://www.amazon' in item_url:
        print ('maybe wrong url...please check...')
        sys.exit()

    base_url = '/'.join(item_url.split('/')[:3])

    percent = 5
    

    #--------------------------  Get Item Top Page Through PhantomJS --------------------------
    status = 'Getting Item Top Page..'

    dcap = dict(DesiredCapabilities.PHANTOMJS)
    dcap["phantomjs.page.settings.userAgent"] = "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/53 (KHTML, like Gecko) Chrome/15.0.87"

    driver = webdriver.PhantomJS(desired_capabilities=dcap)
    item_url = encodingURL(item_url)
    driver.get(item_url)
    WebDriverWait(driver, 5).until(ec.presence_of_all_elements_located)
    html = driver.page_source
    soup = BeautifulSoup(html,'lxml')
    item_title = soup.find(id='productTitle').text.replace(' ', '').replace('\n', '')

    logging.info('got item_url html..')

    # Print Debug
    print ('')
    print ('--- ITEM PAGE ---')
    print ('ITEM TITLE: {}'.format(item_title))
    percent = 10
    

    #--------------------------  Get Review Summary --------------------------
    status = 'Getting Review Summary..'

    reviewSummary = soup.find(id='reviewSummary')
    totalReviewCount = int(reviewSummary.find(class_='totalReviewCount').text.replace(',', ''))
    totalReviewRating = reviewSummary.find(class_='arp-rating-out-of-text').text
    totalReviewRating = transformStarCount(totalReviewRating)
    meter5Star = meter4Star = meter3Star = meter2Star = meter1Star = 0
    try:
        meter5Star = int(reviewSummary.find(class_='a-meter 5star')['aria-label'].split('%')[0])
    except:
        pass
    try:
        meter4Star = int(reviewSummary.find(class_='a-meter 4star')['aria-label'].split('%')[0])
    except:
        pass
    try:
        meter3Star = int(reviewSummary.find(class_='a-meter 3star')['aria-label'].split('%')[0])
    except:
        pass
    try:
        meter2Star = int(reviewSummary.find(class_='a-meter 2star')['aria-label'].split('%')[0])
    except:
        pass
    try:
        meter1Star = int(reviewSummary.find(class_='a-meter 1star')['aria-label'].split('%')[0])
    except:
        pass

    logging.info('got review summary..')

    # Print Debug
    print ('')
    print ('--- CUSTOM REVIEW ---')
    print ('TOTAL REVIEW COUNT: {}'.format(totalReviewCount))
    print ('TOTAL REVIEW RATING: {}'.format(totalReviewRating))
    print ('5 STAR RATIO: |{}{}| {}%'.format('*'*int(20*meter5Star/100), ' '*(20-int(20*meter5Star/100)), meter5Star))
    print ('4 STAR RATIO: |{}{}| {}%'.format('*'*int(20*meter4Star/100), ' '*(20-int(20*meter4Star/100)), meter4Star))
    print ('3 STAR RATIO: |{}{}| {}%'.format('*'*int(20*meter3Star/100), ' '*(20-int(20*meter3Star/100)), meter3Star))
    print ('2 STAR RATIO: |{}{}| {}%'.format('*'*int(20*meter2Star/100), ' '*(20-int(20*meter2Star/100)), meter2Star))
    print ('1 STAR RATIO: |{}{}| {}%'.format('*'*int(20*meter1Star/100), ' '*(20-int(20*meter1Star/100)), meter1Star))
    percent = 15
    

    #-------------------------- Get Review Top Page HTML--------------------------
    status = 'Getting Review Top Page HTML..'

    review_href = reviewSummary.find(id='dp-summary-see-all-reviews')['href']
    review_url = encodingURL(base_url + review_href)
    driver.get(review_url)
    WebDriverWait(driver, 5).until(ec.presence_of_all_elements_located)
    html = driver.page_source
    soup = BeautifulSoup(html,'lxml')
    logging.info('got review top page html..')
    percent = 20
    

    #-------------------------- Get Review All Pages HTML --------------------------
    status = 'Getting Review All Pages HTML..'

    print ('')
    print ('--- GETTING ALL REVIEW PAGES ---')

    page_hrefs = [review_href]
    while True:
        try:
            pagination_bar = soup.find(id='cm_cr-pagination_bar')
            next_page_href = pagination_bar.find(class_='a-last').find('a')['href']
            page_hrefs.append(next_page_href)
            next_page_url = encodingURL(base_url + next_page_href)
            driver.get(next_page_url)
            WebDriverWait(driver, 5).until(ec.presence_of_all_elements_located)
            html = driver.page_source
            soup = BeautifulSoup(html,'lxml')
        except:
            break
    logging.info('got review all page href..')
    print ('found {} pages...'.format(len(page_hrefs)))
    percent = 29

    #-------------------------- Get Each Reviewer DataSeries --------------------------
    status = 'Getting Each Reviewer Data..'

    print ('')
    print ('--- GETTING EACH REVIEW ---')

    columns = ['name', 'score', 'reviewed_at', 'url', 'helpful_votes', 'reviews', 'reviewer_ranking']
    df = pd.DataFrame(columns=columns)

    each_page_percent = round(70/len(page_hrefs))

    for page_href in tqdm(page_hrefs):
            
        page_url = encodingURL(base_url + page_href)
        driver.get(page_url)
        WebDriverWait(driver, 5).until(ec.presence_of_all_elements_located)
        html = driver.page_source
        soup = BeautifulSoup(html,'lxml')
        review_container = soup.find(id='cm_cr-review_list')
        review_boxes = review_container.find_all(class_='a-section review')
        for review in tqdm(review_boxes):

            each_review_percent = round(each_page_percent/len(review_boxes))

            for i in range(3):
                try:
                    star_counts = helpful_votes = reviews = reviewer_ranking = 0
                    author_name = author_href = ''
                    reviewed_at = dt.datetime(2018, 1, 1, 0, 0)

                    star_counts = review.find(class_='a-icon-alt').text
                    star_counts = int(transformStarCount(star_counts))
                    author_name = review.find(class_='author').text
                    author_href = review.find(class_='author')['href']
                    reviewed_at = review.find(class_='review-date').text
                    reviewed_at = transformDateTimestamp(reviewed_at)

                    # Open each reviewer page
                    author_url = encodingURL(base_url + author_href)
                    driver.get(author_url)
                    WebDriverWait(driver, 5).until(ec.presence_of_all_elements_located)
                    html = driver.page_source
                    soup = BeautifulSoup(html,'lxml')
                    helpful_votes = int(soup.find_all(class_='dashboard-desktop-stat')[0].find(class_='dashboard-desktop-stat-value').text.replace(',', ''))
                    reviews = int(soup.find_all(class_='dashboard-desktop-stat')[1].find(class_='dashboard-desktop-stat-value').text.replace(',', ''))
                    reviewer_ranking = int(soup.find(class_=['a-row a-spacing-base']).find(class_='a-row').text.replace('#', '').replace(',', ''))

                except Exception as e:
                    logging.warning('NAME {} TRY {}: CATCH ERRORS, RETRY..'.format(author_name, i+1))
                
                else:
                    break

            else:
                logging.error('--- ERROR! could not found reviewer data ---')
                #logging.info('ERROR TYPE:' + str(type(e)))
                #logging.info('ERROR ARGUMENT:' + str(e.args))
                pass

            logs = '\n' \
                    'author_name: {}\n' \
                    'star_counts: {}\n' \
                    'reviewed_at: {}\n' \
                    'author_url: {}\n' \
                    'helpful_votes: {}\n' \
                    'reviews: {}\n' \
                    'reviewer_ranking: {}\n' \
                    .format(author_name, star_counts, reviewed_at, author_url, helpful_votes, reviews, reviewer_ranking)

            logging.info(logs)

            values = [author_name, star_counts, reviewed_at, author_url, helpful_votes, reviews, reviewer_ranking]
            s = pd.Series(values, index=columns)
            df = df.append(s, ignore_index=True)

            percent += each_review_percent

    logging.info('got all each review..')


    #-------------------------- Process Reviewer DataFrame --------------------------
    status = 'Processing Reviewer Data..'
    logging.info('\n{}'.format(df))
    df['stealth_probability'] = 0
    df['stealth_probability'] = df.apply(lambda x: calcSpyProbability(x['helpful_votes'], x['reviews']), axis=1)
    percent = 99

    #--------------------------  Prediction Stealth Reviewer --------------------------
    status = 'Predicting Stealth Reviewer..'
    print ('')
    print ('')
    print ('--- PREDICTION STEALTH ---')

    wrong_df = df[(df['reviewer_ranking']==0) | ((df['helpful_votes']==0) & (df['reviews']==0))]
    stealth_df = df[df['stealth_probability'] > 0]
    high_stealth_df = df[df['stealth_probability'] == 1]
    low_stealth_df = df[df['stealth_probability'] == 0.5]
    logging.info('\n{}'.format(stealth_df))

    stealth_percentage = int(100*stealth_df['stealth_probability'].sum()/df.shape[0])
    high_probability_stealth_reviwer_count = high_stealth_df.shape[0]
    low_probabilty_stealth_reviewer_count = low_stealth_df.shape[0]
    wrong_data_reviewer_count = wrong_df.shape[0]

    print ('ALL REVIEWER COUNT : {}'.format(df.shape[0]))
    print ('STEALTH PERCENTAGE: {}%'.format(stealth_percentage))
    print ('HIGH PROBABILITY STEALTH REVIEWER COUNT: {}'.format(high_probability_stealth_reviwer_count))
    print ('LOW PROBABILITY STEALTH REVIEWER COUNT: {}'.format(low_probabilty_stealth_reviewer_count))
    print ('WRONG DATA REVIEWER COUNT : {}'.format(wrong_data_reviewer_count))
    

    high_probability_stealth_reviewers = []
    low_probability_stealth_reviewers = []
    wrong_data_reviewers = []

    print ('')
    print ('--- HIGH PROBABILITY STEALTH REVIEWERS ---')
    for index, row in high_stealth_df.iterrows():
        high_probability_stealth_reviewer_dict = {}

        name = row['name']
        score = row['score']
        reviewed_at = str(row['reviewed_at'].isoformat())
        url = row['url']
        helpful_votes = row['helpful_votes']
        reviews = row['reviews']
        reviewer_ranking = row['reviewer_ranking']
        stealth_probability = row['stealth_probability']

        high_probability_stealth_reviewer_dict['name'] = name
        high_probability_stealth_reviewer_dict['score'] = score
        high_probability_stealth_reviewer_dict['reviewed_at'] = reviewed_at
        high_probability_stealth_reviewer_dict['url'] = url
        high_probability_stealth_reviewer_dict['helpful_votes'] = helpful_votes
        high_probability_stealth_reviewer_dict['reviews'] = reviews
        high_probability_stealth_reviewer_dict['reviewer_ranking'] = reviewer_ranking
        high_probability_stealth_reviewer_dict['stealth_probability'] = stealth_probability

        high_probability_stealth_reviewers.append(high_probability_stealth_reviewer_dict)

        print ('*************')
        print ('name: {}'.format(name))
        print ('score: {}'.format(score))
        print ('reviewed_at: {}'.format(reviewed_at))
        print ('href: {}'.format(url))
        print ('helpful_votes: {}'.format(helpful_votes))
        print ('reviews: {}'.format(reviews))
        print ('reviewer_ranking: {}'.format(reviewer_ranking))
        print ('stealth_probability: {}'.format(stealth_probability))

    print ('')
    print ('--- LOW PROBABILITY STEALTH REVIEWERS ---')
    for index, row in low_stealth_df.iterrows():
        low_probability_stealth_reviewer_dict = {}

        name = row['name']
        score = row['score']
        reviewed_at = str(row['reviewed_at'].isoformat())
        url = row['url']
        helpful_votes = row['helpful_votes']
        reviews = row['reviews']
        reviewer_ranking = row['reviewer_ranking']
        stealth_probability = row['stealth_probability']

        low_probability_stealth_reviewer_dict['name'] = name
        low_probability_stealth_reviewer_dict['score'] = score
        low_probability_stealth_reviewer_dict['reviewed_at'] = reviewed_at
        low_probability_stealth_reviewer_dict['url'] = url
        low_probability_stealth_reviewer_dict['helpful_votes'] = helpful_votes
        low_probability_stealth_reviewer_dict['reviews'] = reviews
        low_probability_stealth_reviewer_dict['reviewer_ranking'] = reviewer_ranking
        low_probability_stealth_reviewer_dict['stealth_probability'] = stealth_probability

        low_probability_stealth_reviewers.append(low_probability_stealth_reviewer_dict)
        
        print ('*************')
        print ('name: {}'.format(row['name']))
        print ('score: {}'.format(row['score']))
        print ('reviewed_at: {}'.format(row['reviewed_at']))
        print ('href: {}'.format(row['url']))
        print ('helpful_votes: {}'.format(row['helpful_votes']))
        print ('reviews: {}'.format(row['reviews']))
        print ('reviewer_ranking: {}'.format(row['reviewer_ranking']))
        print ('stealth_probability: {}'.format(row['stealth_probability']))

    print ('')
    print ('--- WRONG DATA REVIEWERS ---')
    for index, row in wrong_df.iterrows():
        wrong_data_reviewer_dict = {}

        name = row['name']
        score = row['score']
        reviewed_at = str(row['reviewed_at'].isoformat())
        url = row['url']
        helpful_votes = row['helpful_votes']
        reviews = row['reviews']
        reviewer_ranking = row['reviewer_ranking']
        stealth_probability = row['stealth_probability']

        wrong_data_reviewer_dict['name'] = name
        wrong_data_reviewer_dict['score'] = score
        wrong_data_reviewer_dict['reviewed_at'] = reviewed_at
        wrong_data_reviewer_dict['url'] = url
        wrong_data_reviewer_dict['helpful_votes'] = helpful_votes
        wrong_data_reviewer_dict['reviews'] = reviews
        wrong_data_reviewer_dict['reviewer_ranking'] = reviewer_ranking
        wrong_data_reviewer_dict['stealth_probability'] = stealth_probability

        wrong_data_reviewers.append(wrong_data_reviewer_dict)


        print ('*************')
        print ('name: {}'.format(row['name']))
        print ('score: {}'.format(row['score']))
        print ('reviewed_at: {}'.format(row['reviewed_at']))
        print ('href: {}'.format(row['url']))
        print ('helpful_votes: {}'.format(row['helpful_votes']))
        print ('reviews: {}'.format(row['reviews']))
        print ('reviewer_ranking: {}'.format(row['reviewer_ranking']))
        print ('stealth_probability: {}'.format(row['stealth_probability']))
    
    percent = 100
    status = 'Complete'


    driver.quit()


if __name__ == '__main__':
    main()