#!/usr/bin/env python
# coding: utf-8

# In[13]:


import json
import pandas as pd
import numpy as np
import re
from sqlalchemy import create_engine
from config import db_password
import time


# In[14]:


file_dir = 'c:/Users/Femi/'


# In[15]:


with open(f'{file_dir}/wikipedia.movies.json', mode='r') as file:
    wiki_movies_raw = json.load(file)
kaggle_metadata = pd.read_csv(f'{file_dir}movies_metadata.csv',low_memory = False)
ratings = pd.read_csv(f'{file_dir}ratings.csv')


# In[16]:


# Modify json file by creating a filter expression for only movies with a director and an IMDb
wiki_movies = [movie for movie in wiki_movies_raw
               if ('Director' in movie or 'Directed by' in movie)
                   and 'imdb_link' in movie
                   and 'No. of episodes' not in movie]


# In[20]:


def clean_movie(movie):
    movie = dict(movie) #create a non-destructive copy
    alt_titles = {}
    # combine alternate titles into one list
    for key in ['Also known as','Arabic','Cantonese','Chinese','French',
                'Hangul','Hebrew','Hepburn','Japanese','Literally',
                'Mandarin','McCune-Reischauer','Original title','Polish',
                'Revised Romanization','Romanized','Russian',
                'Simplified','Traditional','Yiddish']:
        if key in movie:
            alt_titles[key] = movie[key]
            movie.pop(key)
    if len(alt_titles) > 0:
        movie['alt_titles'] = alt_titles

    # merge column names
    def change_column_name(old_name, new_name):
        if old_name in movie:
            movie[new_name] = movie.pop(old_name)
    change_column_name('Adaptation by', 'Writer(s)')
    change_column_name('Country of origin', 'Country')
    change_column_name('Directed by', 'Director')
    change_column_name('Distributed by', 'Distributor')
    change_column_name('Edited by', 'Editor(s)')
    change_column_name('Length', 'Running time')
    change_column_name('Original release', 'Release date')
    change_column_name('Music by', 'Composer(s)')
    change_column_name('Produced by', 'Producer(s)')
    change_column_name('Producer', 'Producer(s)')
    change_column_name('Productioncompanies ', 'Production company(s)')
    change_column_name('Productioncompany ', 'Production company(s)')
    change_column_name('Released', 'Release Date')
    change_column_name('Release Date', 'Release date')
    change_column_name('Screen story by', 'Writer(s)')
    change_column_name('Screenplay by', 'Writer(s)')
    change_column_name('Story by', 'Writer(s)')
    change_column_name('Theme music composer', 'Composer(s)')
    change_column_name('Written by', 'Writer(s)')

      
    return movie
def Extract_Transform_Load(wikipedia_file_name, kaggle_file, ratings_file):
    with open(wikipedia_file_name, mode='r') as file:
        wiki_movies_raw = json.load(file)
    kaggle_metadata = pd.read_csv(kaggle_file,low_memory = False)
    ratings = pd.read_csv(ratings_file)
    
    # Modify json file by creating a filter expression for only movies with a director and an IMDb
    
    wiki_movies = [movie for movie in wiki_movies_raw
               if ('Director' in movie or 'Directed by' in movie)
                   and 'imdb_link' in movie
                   and 'No. of episodes' not in movie]
    
    
    
# list comprehension to make a list of cleaned movies  and re_create wiki_movies_df
    clean_movies = [clean_movie(movie) for movie in wiki_movies]
    wiki_movies_df = pd.DataFrame(clean_movies)

## Extract IMDb from the IMDb link & drop duplicates
    try:
        
        wiki_movies_df['imdb_id'] = wiki_movies_df['imdb_link'].str.extract(r'(tt\d{7})')
        wiki_movies_df.drop_duplicates(subset='imdb_id', inplace=True)
        
    except Exception as e:
        print(e)
   
# Select columns to keep from dataframe
    wiki_columns_to_keep = [column for column in wiki_movies_df.columns if wiki_movies_df[column].isnull().sum() < len(wiki_movies_df) * 0.9]
    wiki_movies_df = wiki_movies_df[wiki_columns_to_keep]

#Next , we need to check the columns for inconsistent data type and convert.using .dtypes. Box office, budget, running time should be numeric while release date should be a date object
## For box column, create a data series that drops missing values
    box_office = wiki_movies_df['Box office'].dropna() 

#To ensure all box office data is entered as a string 
    box_office = box_office.apply(lambda x: ' '.join(x) if type(x) == list else x)
    box_office = box_office.str.replace(r'\$.*[-—–](?![a-z])', '$', regex=True)

#Box office should be numeric values
# Create variable and set to the finished regular expression string for converting the dollar amounts to numeric values
    form_one = r'\$\s*\d+\.?\d*\s*[mb]illi?on'
    form_two = r'\$\s*\d{1,3}(?:[,\.]\d{3})+(?!\s[mb]illion)'

# create function to parse the dollar values
    def parse_dollars(s):
    # if s is not a string, return NaN
        if type(s) != str:
            return np.nan

    # if input is of the form $###.# million
        if re.match(r'\$\s*\d+\.?\d*\s*milli?on', s, flags=re.IGNORECASE):

        # remove dollar sign and " million"
            s = re.sub('\$|\s|[a-zA-Z]','', s)

        # convert to float and multiply by a million
            value = float(s) * 10**6

        # return value
            return value

    # if input is of the form $###.# billion
        elif re.match(r'\$\s*\d+\.?\d*\s*billi?on', s, flags=re.IGNORECASE):

        # remove dollar sign and " billion"
            s = re.sub('\$|\s|[a-zA-Z]','', s)

        # convert to float and multiply by a billion
            value = float(s) * 10**9

        # return value
            return value

    # if input is of the form $###,###,###
        elif re.match(r'\$\s*\d{1,3}(?:[,\.]\d{3})+(?!\s[mb]illion)', s, flags=re.IGNORECASE):

        # remove dollar sign and commas
            s = re.sub('\$|,','', s)

        # convert to float
            value = float(s)

        # return value
            return value

    # otherwise, return NaN
        else:
            return np.nan
    
# Parse the box office data to numeric values
    wiki_movies_df['box_office'] = box_office.str.extract(f'({form_one}|{form_two})', flags=re.IGNORECASE)[0].apply(parse_dollars)

## We no longer need the Box Office column, so we’ll just drop it:
    wiki_movies_df.drop('Box office', axis=1, inplace=True)

# Budget column
#Create a budget variable with the following code:
    budget = wiki_movies_df['Budget'].dropna()

#Convert any lists to strings:
    budget = budget.map(lambda x: ' '.join(x) if type(x) == list else x)

#Then remove any values between a dollar sign and a hyphen (for budgets given in ranges):
    budget = budget.str.replace(r'\$.*[-—–](?![a-z])', '$', regex=True)

#Parse the budget values column
    wiki_movies_df['budget'] = budget.str.extract(f'({form_one}|{form_two})', flags=re.IGNORECASE)[0].apply(parse_dollars)

#Drop the original budget value
    wiki_movies_df.drop('Budget', axis=1, inplace=True)

#release date column
#Parse the release date column
    release_date = wiki_movies_df['Release date'].dropna().apply(lambda x: ' '.join(x) if type(x) == list else x)

# Create variable and set to the finished regular expression string for converting the date format
    date_form_one = r'(?:January|February|March|April|May|June|July|August|September|October|November|December)\s[123]\d,\s\d{4}'
    date_form_two = r'\d{4}.[01]\d.[123]\d'
    date_form_three = r'(?:January|February|March|April|May|June|July|August|September|October|November|December)\s\d{4}'
    date_form_four = r'\d{4}'

#Extracting date and converting 
    wiki_movies_df['release_date'] = pd.to_datetime(release_date.str.extract(f'({date_form_one}|{date_form_two}|{date_form_three}|{date_form_four})')[0], infer_datetime_format=True)

# Parse the run_time column
    running_time = wiki_movies_df['Running time'].dropna().apply(lambda x: ' '.join(x) if type(x) == list else x)
    running_time_extract = running_time.str.extract(r'(\d+)\s*ho?u?r?s?\s*(\d*)|(\d+)\s*m')
    running_time_extract = running_time_extract.apply(lambda col: pd.to_numeric(col, errors='coerce')).fillna(0)

# Function to convert data to Dataframe and drop original running time data
    wiki_movies_df['running_time'] = running_time_extract.apply(lambda row: row[0]*60 + row[1] if row[2] == 0 else row[2], axis=1)
    wiki_movies_df.drop('Running time', axis=1, inplace=True)
    
    # Cleaning the kaggle Data
#The following code will keep rows where the adult column is False, and then drop the adult column
    kaggle_metadata = kaggle_metadata[kaggle_metadata['adult'] == 'False'].drop('adult',axis='columns')

## checking the values of the video column
    kaggle_metadata['video'] = kaggle_metadata['video'] == True

#For the numeric columns, we can just use the to_numeric() method from Pandas. We’ll make sure the errors= argument is set to 'raise', so we’ll know if there’s any data that can’t be converted to numbers
    kaggle_metadata['budget'] = kaggle_metadata['budget'].astype(int)
    kaggle_metadata['id'] = pd.to_numeric(kaggle_metadata['id'], errors='raise')
    kaggle_metadata['popularity'] = pd.to_numeric(kaggle_metadata['popularity'], errors='raise')

##Convert release_date to datetime
    kaggle_metadata['release_date'] = pd.to_datetime(kaggle_metadata['release_date'])

#Assign to_datetime to timestamp column
    ratings['timestamp'] = pd.to_datetime(ratings['timestamp'], unit='s')
#Clean the rating Data

##Use to_datetime to convert the timestamp column in the ratings data
    ratings['timestamp'] = pd.to_datetime(ratings['timestamp'], unit='s')

#Use a groupby on the “movieId” and “rating” columns and take the count for each group
    rating_counts = ratings.groupby(['movieId','rating'], as_index=False).count()                 .rename({'userId':'count'}, axis=1) 

##pivot this data so that movieId is the index, the columns will be all the rating values, and the rows will be the counts for each rating value
    rating_counts = ratings.groupby(['movieId','rating'], as_index=False).count()                 .rename({'userId':'count'}, axis=1)                 .pivot(index='movieId',columns='rating', values='count')

#rename columns using a list of comprehension
    rating_counts.columns = ['rating_' + str(col) for col in rating_counts.columns]

#Merge Wikipedia, Kaggle and Ratings Data

##Merge Wikipedia  Kaggle Data
    movies_df = pd.merge(wiki_movies_df, kaggle_metadata, on='imdb_id', suffixes=['_wiki','_kaggle'])

##Drop colums
    movies_df.drop(columns=['title_wiki','release_date_wiki','Language','Production company(s)'], inplace=True)
    def fill_missing_kaggle_data(df, kaggle_column, wiki_column):
        df[kaggle_column] = df.apply(
            lambda row: row[wiki_column] if row[kaggle_column] == 0 else row[kaggle_column]
            , axis=1)
        df.drop(columns=wiki_column, inplace=True)
    
    fill_missing_kaggle_data(movies_df, 'runtime', 'running_time')
    fill_missing_kaggle_data(movies_df, 'budget_kaggle', 'budget_wiki')
    fill_missing_kaggle_data(movies_df, 'revenue', 'box_office')


##Check that there are no columns with only one value
    for col in movies_df.columns:
        lists_to_tuples = lambda x: tuple(x) if type(x) == list else x
        value_counts = movies_df[col].apply(lists_to_tuples).value_counts(dropna=False)
        num_values = len(value_counts)
        if num_values == 1:
            print(col)


#reorder columns
    movies_df = movies_df.loc[:, ['imdb_id','id','title_kaggle','original_title','tagline','belongs_to_collection','url','imdb_link',
                       'runtime','budget_kaggle','revenue','release_date_kaggle','popularity','vote_average','vote_count',
                       'genres','original_language','overview','spoken_languages','Country',
                       'production_companies','production_countries','Distributor',
                       'Producer(s)','Director','Starring','Cinematography','Editor(s)','Writer(s)','Composer(s)','Based on'
                      ]]

#rename colums for consistency 
    movies_df.rename({'id':'kaggle_id',
                  'title_kaggle':'title',
                  'url':'wikipedia_url',
                  'budget_kaggle':'budget',
                  'release_date_kaggle':'release_date',
                  'Country':'country',
                  'Distributor':'distributor',
                  'Producer(s)':'producers',
                  'Director':'director',
                  'Starring':'starring',
                  'Cinematography':'cinematography',
                  'Editor(s)':'editors',
                  'Writer(s)':'writers',
                  'Composer(s)':'composers',
                  'Based on':'based_on'
                 }, axis='columns', inplace=True)

## Merge rating counts into movies_df
    movies_with_ratings_df = pd.merge(movies_df, rating_counts, left_on='kaggle_id', right_index=True, how='left')

#Fill unrated movies with zeros. This is the data to load into SQL
    movies_with_ratings_df[rating_counts.columns] = movies_with_ratings_df[rating_counts.columns].fillna(0)
## Create the Database Engine that will allow pandas to communicate with sql server
# Using this format "postgres://[user]:[password]@[location]:[port]/[database]"

    db_string = f"postgres://postgres:{db_password}@127.0.0.1:5432/movie_data"
    engine = create_engine(db_string)

# Import the Movie Data
    movies_df.to_sql(name='movies', con=engine, if_exists='replace')
    print('here')
    rows_imported = 0
    try:
        for data in pd.read_csv(f'{file_dir}ratings.csv', chunksize=1000000):

            print(f'importing rows {rows_imported} to {rows_imported + len(data)}...', end='')
            data.to_sql(name='ratings', con=engine, if_exists='append')
            rows_imported += len(data)

            print(f'Done.')
    except Exception as e:
        print(e)



# In[21]:


file_dir = 'c:/Users/Femi/'
wikipedia_file_name=f'{file_dir}/wikipedia.movies.json'
kaggle_file_name=f'{file_dir}movies_metadata.csv'
ratings_file_name=f'{file_dir}ratings.csv'

Extract_Transform_Load(wikipedia_file_name,kaggle_file_name,ratings_file_name)


