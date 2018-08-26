
# coding: utf-8

# In[1]:


import requests
from bs4 import BeautifulSoup
import json
from urllib.request import urlopen
import re
import collections
import time
import pandas as pd
from tqdm import tqdm
import pickle
import random


# import urls

#url = 'https://api.bazaarvoice.com/data/reviews.json?Filter=ProductId%3AP416341&Sort=CampaignId%3Aasc&Limit=100&Offset=0&Include=Products%2CComments&Stats=Reviews&passkey=rwbw526r2e7spptqd2qzbkp7&apiversion=5.4'
#url = 'https://www.sephora.com/shop/moisturizing-cream-oils-mists?pageSize=300&currentPage=1'
# https://www.sephora.com/product/your-skin-but-better-cc-cream-spf-50-P411885?skuId=1868165


# # Scrape product ID for all moisturizers on Sephora

# In[2]:


# scrape product name, id and URL for all moisturizers

scripts = []
productId = []
productName = []
productUrl = []
productPrice = []


for i in [1,2,3]:
    url = 'https://www.sephora.com/shop/moisturizing-cream-oils-mists?pageSize=300&currentPage='+str(i)
    response = requests.get(url)
    page = response.text
    soup = BeautifulSoup(page,"lxml")
    scripts += str([i.text for i in soup.find_all('script') if 'priceCurrency' in i.text])
    
    pattern = re.compile('\"(productId)\":\"(.*?)\"')
    fields = re.findall(pattern, str([i.text for i in soup.find_all('script') if 'Sephora Unified Link Component' in i.text]))
    productId += [list(i)[1] for i in fields]
    
    pattern = re.compile('\"(url)\":\"(.*?)\"')
    fields = re.findall(pattern, str([i.text for i in soup.find_all('script') if 'priceCurrency' in i.text]))
    productUrl += [list(i)[1] for i in fields]
    
    pattern = re.compile('\"(price|highPrice)\":\"(.*?)\"')
    fields = re.findall(pattern, str([i.text for i in soup.find_all('script') if 'priceCurrency' in i.text]))
    productPrice += [list(i)[1] for i in fields] 
    
    pattern = re.compile('\"(Product)\",\"(name)\":\"(.*?)\"')
    fields = re.findall(pattern, str([i.text for i in soup.find_all('script') if 'priceCurrency' in i.text]))
    productName += [list(i)[2] for i in fields]


# In[3]:


# save product info

product = pd.DataFrame([productName,productId,productPrice,productUrl]).T

with open('product.pickle', 'wb') as fp:
            pickle.dump(product, fp)


# # Read user reviews via Bazaarvoice API

# In[235]:


# get reviews from bazaarvoice api

# reviewlist_all = []
# product_all = []
success_id = []
fail_id = []


for i in tqdm(productId[360:460]):
    try:
        reviewlist = []
        review_count = 0
        offset=0

        #url ='https://api.bazaarvoice.com/data/reviews.json?Filter=ProductId%3AP416341&Sort=CampaignId%3Aasc&Limit=100&Offset=0&Include=Products%2CComments&Stats=Reviews&passkey=rwbw526r2e7spptqd2qzbkp7&apiversion=5.4'
        url = 'https://api.bazaarvoice.com/data/reviews.json?Filter=ProductId%3A'+i+                '&Sort=Helpfulness%3Aasc&Limit=100&Offset='+str(0)+                '&Include=Products%2CComments&Stats=Reviews&passkey=rwbw526r2e7spptqd2qzbkp7&apiversion=5.4'
        response = requests.get(url)
        page = response.text
        a = json.loads(response.content.decode('utf-8'))

        # extract data
        ids = [key for key in a['Includes']['Products']]
        product = a['Includes']['Products'][ids[0]]
        product['product_id'] = i
        product_all.append(product)

        total_review_count = a['TotalResults']
        reviewlist += a['Results']
        review_count = len(reviewlist)
        offset = review_count

        while review_count < total_review_count:
            url = 'https://api.bazaarvoice.com/data/reviews.json?Filter=ProductId%3A'+i+                    '&Sort=Helpfulness%3Aasc&Limit=100&Offset='+str(offset)+                    '&Include=Products%2CComments&Stats=Reviews&passkey=rwbw526r2e7spptqd2qzbkp7&apiversion=5.4'
            response = requests.get(url)
            page = response.text
            a = json.loads(response.content.decode('utf-8'))
            reviewlist += a['Results']
            review_count = len(reviewlist)
            offset = review_count
            time.sleep(random.sample(range(9),1)[0])

        for r in reviewlist:
            r['product_id']=i

        reviewlist_all += reviewlist

        with open('reviewlist_all.pickle', 'wb') as fp:
                    pickle.dump(reviewlist_all, fp)
                
        success_id.append(i)
        
    except:
        fail_id.append(i)


# In[236]:


# check data
print('total product:', len(product_all))
print('total reviews:', len(reviewlist_all))
print('failed ids:',fail_id)


# In[237]:


# pickle all reviews and products 
with open('reviewlist_all.pickle', 'wb') as fp:
    pickle.dump(reviewlist_all, fp)
    
with open('product_all.pickle', 'wb') as fp:
    pickle.dump(product_all, fp)


# In[258]:


# Example - frequency of incentivized reviews
a = [i['ContextDataValues']['IncentivizedReview']['Value'] 
     for i in reviewlist_all if 'IncentivizedReview' in i['ContextDataValues']]
collections.Counter(a)


# # NOT IN USE - Scrape individual product page on Sephora

# In[4]:


# function to scrape product page

def get_product_page(x):
    try:
        response = requests.get(x)
        page = response.text
        soup = BeautifulSoup(page,"lxml")
        soup_bowl.append(str(soup))
        success_url.append(i)
    except:
        fail_url.append(i)


# In[87]:


# scrape detailed product info 

soup_bowl = []
success_url = []
fail_url = []
n=1

for i in tqdm(productUrl):
    get_product_page(i)
    n+=1
    
    if n==10:
        with open('soup_bowl.pickle', 'wb') as fp:
            pickle.dump(soup_bowl, fp)
        n=1
 
    #result = pd.concat(all_flight)
    time.sleep(random.sample(range(9),1)[0])


# In[ ]:


# extract size and price pair
productSize = []
productSizeP = []

for i in soup_bowl:
    pattern = re.compile('\"(size)\":\"(.*?)\"')
    fields = re.findall(pattern, i)
    productSize.append([list(a)[1] for a in re.findall(pattern, i)])

    pattern = re.compile('\"(listPrice)\":\"(.*?)\"')
    fields = re.findall(pattern, soup_bowl[7])
    productSizeP.append([list(a)[1] for a in re.findall(pattern, i)])

    #print(dict(zip(size,price)))


# In[222]:


url = 'https://api.bazaarvoice.com/data/reviews.json?Filter=ProductId%3A'+productId[224]+            '&Sort=Helpfulness%3Aasc&Limit=100&Offset='+str(0)+            '&Include=Products%2CComments&Stats=Reviews&passkey=rwbw526r2e7spptqd2qzbkp7&apiversion=5.4'
response = requests.get(url)
page = response.text
a = json.loads(response.content.decode('utf-8'))

