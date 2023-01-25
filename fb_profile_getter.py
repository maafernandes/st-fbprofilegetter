from pyfacebook import GraphAPI, FacebookApi
import lxml
import json
import pandas as pd
import streamlit as st
from streamlit_agraph import agraph, Node, Edge, Config
import os
import numpy as np
import requests 
import datetime

USER_ID = "119042924349576"
APP_ID = "695320508682752"  # Your App ID
APP_SECRET = "baa06e8df14ae4e4c42295f1c988ffe5"  # Your App secret
os.environ['OAUTHLIB_INSECURE_TRANSPORT'] = '1'
USER_ACCESS_TOKEN = "EAAJ4YZBvs0gABADAVzdkMa7WeKkCjpBzlCOB2qidW0kpAAWLYkFZAm7hU1uboHBLdcEWbY3uL7TTZBUoBSeDf70Qy7FLri0YZC4qZAjHJC7wLnoQZBzmZCoAx0YRFCXQ3b8BizyEZBLUakxawt5Hd3j32aKugxR2yTht9uH9baJFrax6rOKSf4KSwiBX8TIHDiAA2X3IzdCgbiZCvasguzskDZBq1gSUcncKhhXA1xAlaKDVMNZBenBKpjn"  # Your Access Token
##APP_TOKEN = "695320508682752|5gcbMLfSulu2lxt1X3dCGYCRG4I"
##PAGE_TOKEN = "EAAJ4YZBvs0gABAFJuE0pyvc7N9tWwZBwl1ftIGb9YAfYZAzXwt1uZANKZAtvQfJ4LfdXckv6raAuNYkkxNrivnhwqbzt5Kv5VE0ylNqz1Bj0nn5V0cOP5VrvAravwT9q8HsVTTfLd1eEns9vuAi7S2fbqXINFScuTltRO1wRhIrALqsj2vPDn6ObWywe9PWOPGfZADmJB12nCHtzLOUOtN"
url_me = "https://graph.facebook.com/v.15/me?acess_token=" + USER_ACCESS_TOKEN

api = GraphAPI(
    app_id=APP_ID, 
    app_secret=APP_SECRET,
    access_token=USER_ACCESS_TOKEN
)
fb = FacebookApi(
    app_id=APP_ID, 
    app_secret=APP_SECRET,
    access_token=USER_ACCESS_TOKEN
)
## developer profile

def get_user_profile():
    #print(api.get_object(USER_ID, 'first_name'))
    fields = ['name','id','email','birthday','location']
    f = ",".join(fields)
    user = api.get_objects(USER_ID, f)
    return list(user)



##test users -app NONE
TOKEN1 = 'EAAJ4YZBvs0gABANtYrvEARsMTatgTXBl2DXEhrOBp0ZB95w6uXuBEQGMXiDDMWWIeTR6a2ZBJCMmuM12OkmL7atv03li8uwB4OrRXobkomoiLldz3CkibEFQulHTU6VNb36zqC7WHcNDeRDhfyVsMQstSwf5Uti5QpmFrMtP9g8nEanJp3ZBLJO1YTgCp2fn9EIViFGNnQZDZD'
test1_ID = '105465549066078'
#api_test1 = GraphAPI(
   # app_id=test1_ID, 
    #app_secret=APP_SECRET,
    #access_token=TOKEN1)    
#test1 = api_test1.get_object(test1_ID, 'first_name')
#friends1 = api_test1.get_full_connections(object_id=test1_ID, connection="friends")
#print(test1)
#print(friends1)

##subscriptions
def get_subs():
    subs = fb.user.get_accounts(user_id=USER_ID)
    data=[]
    field = 0
    page_name=[]
    for data in subs.data:
      page_name.append(subs.data[field].name) 
      field=field+1
    return page_name
##likes by name
def get_likes():
    boraver= []
    x=0
    thisdict=api.get_full_connections(object_id=USER_ID, connection="likes")
    for data in thisdict['data']:
        like_name = data['name']
        boraver.append(like_name) 
    return boraver



## [---------STREAMLIT CONFIG----------------]




#st.write(user)
#st.write(app)

DATE_COLUMN = 'date/time'
FB_URL = "https://graph.facebook.com/v15.0/me?fields=likes&access_token=" + USER_ACCESS_TOKEN
DATA_URL = ('https://s3-us-west-2.amazonaws.com/'
         'streamlit-demo-data/uber-raw-data-sep14.csv.gz')

##graph build
def graphbuild():
    nodes=[]
    edges=[]
    nodes.append(Node (id = USER_ID, title = 'user', size =25))
    nodes.append(Node (id = 'Pages', size = 25))
    nodes.append(Node (id = 'Friends', size = 25))
    nodes.append(Node (id = 'Likes', size = 25 ))

    edges.append( Edge (source = USER_ID, label= 'owns page', target='Pages'))
    edges.append( Edge (source = USER_ID, label= 'has liked', target='Likes'))
    edges.append( Edge (source = USER_ID, label= 'has become friends with', target='Friends'))
    ## add nodes/edges for page owned
    subs = get_subs()
    i=0
    for k in subs :
            nodes.append(Node (id = subs[i], size = 25 ))
            edges.append(Edge(source = 'Pages', target = subs[i]))
            i=i+1
    ## add nodes/edges for liked pages 
    liked = get_likes()
    i=0
    for k in liked :
            nodes.append(Node(id = liked[i] + 'lk'  , size = 25 ))
            edges.append(Edge(source = 'Likes', target = liked[i] ))
            i=i+1
    #for nodes/edges of friends

    config = Config(width=500,
                height = 500)
    
    return agraph(nodes=nodes, edges = edges, config=config)

def graph_initial():
    object = GraphAPI(access_token= USER_ACCESS_TOKEN)
    return object
## page
user_data = pd.DataFrame (api.get_objects(USER_ID, []))
st.markdown("# Profile Analytics for Facebook ")
col1, col2 = st.columns([1,2])
col1.markdown('User:' + st.write(pd.DataFrame(api.get_objects(USER_ID, ['first_name', 'location'])))
)
with col1.container():
      col1.write('Aqui vai aparecer input de Token e ID //depois da submissão vai aparecer dataframe com detaisl do perfil' )
col2.markdown("Social Graph")
with col2.container():
    col2.write(graphbuild())

st.markdown("---")
 



@st.cache
def load_data(nrows):
    #scrapper_data = pd.read_html(FB_URL)
    df = pd.DataFrame(data)
    return df
    #lowercase = lambda x: str(x).lower()
    #data.rename(lowercase, axis='columns', inplace=True)
    #ata[DATE_COLUMN] = pd.to_datetime(data[DATE_COLUMN])
   
st.dataframe(load_data(10))
if st.checkbox('Show raw data'):
    st.subheader('Raw data')
    #st.write(data)

col3, col4 = st.columns([1,1])
col3.markdown("Timeline of Activity")
col4.markdown("Map of Actions")
# Create a text element and let the reader know the data is loading.
#data_load_state = st.text('Loading data...')
# Load 10,000 rows of data into the dataframe.
# Notify the reader that the data was successfully loaded.
#data_load_state.text("Done! (using st.cacher)")
##st.write(data)

#hour_to_filter = st.slider('hour', 0, 23, 17)
#filtered_data = data[data[DATE_COLUMN].dt.hour == hour_to_filter]
#st.subheader(f'Map of all pickups at {hour_to_filter}:00')
#st.map(filtered_data)


#getFacebookPageCommentData(post_id, access_token, 1)["comments"]["data"][0]["from"]


##print(app_token)
##print(api)


#api.get_connection(object_id=fb.app_id, connection = '"posts"')


#api.__init__(app_id = api.app_id, app_secret = api.app_secret, access_token = api.access_token, application_only_auth= False, oauth_flow= False, sleep_on_rate_limit = True)

#response = api._request( url= url_me, verb = "GET", auth_need= True)
#print(response)

#app_token = "2996202927351871|kHyqUbmBYkY_6-l8x2mT1TwDf8Q"
#page_token = "EAAqlB9so6D8BAMTUg2Dfv3UlQHyz4cZBy9uEXQuqzePwEzQge11TibvU4AuHTdMNZBGSAUJdg1NykSglF6Lk9zG3895vChj5j1MVN2m77wsZCmMfECvTwlTVZCOqF0ZAlwoHNXznqjGtREvt7oZAYXceZB7mZBtK82ikJXiiqmYOdKgf3UzC4DPWXptXUGHeK6tJmL37V98OLTyxtddF0tic"
#user = api.get_object(object_id = api.app_id)
#print(user)

#user_posts = api.get_connection(object_id = api.app_id, connection = 'posts')
#api.get_connection(object_id = api.app_id, connection = "posts")









