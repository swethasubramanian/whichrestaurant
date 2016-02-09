# Restaurant recommender system in madison, WI
import pandas as pd
import numpy as np
from bokeh.charts import Bar, BoxPlot, output_file, output_server, show, vplot
from bokeh.plotting import figure
from bokeh.embed import components
from collections import defaultdict
from flask import Flask, render_template, request, redirect, url_for

app = Flask(__name__)

filenames = ['yelp_academic_dataset_business.json',
             'yelp_academic_dataset_checkin.json',
             'yelp_academic_dataset_review.json',
             'yelp_academic_dataset_tip.json',
             'yelp_academic_dataset_user.json']

def formatData(filename):
    with open(filename, 'rb') as f:
        data = f.readlines()

    # remove trailing new line '\n'
    data = map(lambda x: x.rstrip(), data)
    return "[" + ','.join(data) + "]"

def reduceData():
    # now, load it into pandas
    businessDf = pd.read_json(formatData(filenames[0]))
    checkinDf = pd.read_json(formatData(filenames[1]))
    #reviewDf = pd.read_json(formatData(filenames[2]))
    tipDf = pd.read_json(formatData(filenames[3]))
    userDf = pd.read_json(formatData(filenames[4]))

    # Find businesses in Madison, WI
    businessDf = businessDf[businessDf.city == 'Madison']

    # Find businesses that are open?
    businessDf = businessDf[businessDf.open == True]

    # Find businesses that deal with food!
    businessDf = businessDf[businessDf['categories'].astype(str).str.contains("Restaurants")]
    businessIDs = list(set(businessDf.business_id))
    checkinDf = checkinDf[checkinDf.business_id.isin(businessDf.business_id)]
    tipDf = tipDf[tipDf.business_id.isin(businessDf.business_id)]
    #reviewDf = reviewDf[reviewDf.business_id.isin(businessDf.business_id)]

    # pickle the reviews (huge data set)
    #reviewDf.to_pickle('review.pkl')

    reviewDf = pd.read_pickle('review.pkl')
    # Minimize userdf too
    userDf = userDf[userDf.user_id.isin(reviewDf.user_id)]

    ## Complie a list of business categories
    categories = []
    for category in businessDf['categories']:
        categories.extend(category)
    categories = list(set(categories))

    # Focus on certain categories (ones I prefer)
    prefCategories = ['Mexican', 'Thai', 'Chinese', 'Sushi Bars', 'Breakfast & Brunch', 'Italian', 'Pizza']
    df = businessDf[businessDf['categories'].astype(str).str.contains("Indian")]
    for category in prefCategories:
        df2 = businessDf[businessDf.categories.astype(str).str.contains(category)]
        df = pd.concat([df, df2])
    prefCategories.append('Indian')
    origBusinessDf = businessDf
    businessDf = df

    ## Add another column called category_id
    businessDf['category_id'] = ''
    for category in prefCategories:
        businessDf.category_id[businessDf.categories.astype(str).str.contains(str(category))] = category
    categories = list(set(categories))
    categories.remove('Restaurants')


    # number of restaurants per category
    restPerCategory = defaultdict(list)

    #Most popular cuisines
    # Use number of reviews to assess popularity.
    reviewDf = reviewDf[reviewDf.business_id.isin(businessDf.business_id)]
    reviewDf = reviewDf.merge(businessDf[['business_id', 'category_id']], on = ['business_id'])

    reviewDf['usefulness'] = reviewDf.votes.apply(lambda x: x['useful'])

    #  weight every restaurant based on the 'usefulness' of review
    # also on read tips for every restaurant
    businessIDs = list(set(businessDf.business_id))
    businessDf['weighted_star'] = ''
    businessDf['avg_star'] = ''
    for business in businessIDs:
        a = reviewDf[reviewDf.business_id == business]
        businessDf.avg_star[businessDf.business_id== business] = np.mean(a.stars)
        businessDf.weighted_star[businessDf.business_id== business] = \
            np.sum(np.multiply(a.stars, np.array(a.usefulness)+1.0))/\
            np.sum(np.array(a.usefulness)+1.0)
    reviewDf.to_pickle('review2.pkl')
    businessDf.to_pickle('business2.pkl')


@app.route('/')
def main():
    return redirect('/index')


@app.route('/index', methods = ['GET', 'POST'])
def index():
    if request.method == 'GET':
        return render_template('index.html')
    else:
        woo = request.form['cuisine']
        make_plot(woo)
        return render_template('plots.html')
    
def make_plot(which_cuisine):
    reviewDf = pd.read_pickle('review2.pkl')
    businessDf = pd.read_pickle('business2.pkl')
   # best indian restaurant
    p4 = Bar(businessDf[businessDf.category_id == which_cuisine], values = 'avg_star',\
             label = 'name', agg = 'max', color = "wheat", \
             title = 'Best '+which_cuisine+' by star rating alone', \
             xlabel = 'Restaurant name', ylabel = 'Star rating')
    output_file("templates/plots.html")
    #p = vplot(p4)
    show(p4)
    


if __name__ == '__main__':
    app.run( debug = True)
    #main()






