## Sentiment analysis for reviews
import pandas as pd
import numpy as np
from bokeh.charts import Bar, BoxPlot, output_file, output_server, show, vplot
from bokeh.plotting import figure
from bokeh.embed import components
from collections import defaultdict

reviewDf = pd.read_pickle('review2.pkl')
businessDf = pd.read_pickle('business2.pkl')

from nltk.corpus import stopwords
stopset = set(stopwords.words('english'))

words = defaultdict(list)
for i in reviewDf.index:
    a = [e.lower() for e in reviewDf.text[i].split() if len(e) >= 3]
    #a = reviewDf.text[i].split()
    b = set(stopset & set(a))
    for x in b:
        a.remove(x)
    words[list(set(businessDf[businessDf.business_id == \
        reviewDf.business_id[i]].name))[0]].append(a)
#output_file("plot.html")
#p = Bar(values = words.values()[1], agg = 'count')
#show(p)



