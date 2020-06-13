# Movies_ETL

The purpose of this project is to write a script to extract, transform and load the provided data.  This script will be automated to carry out the ETL proces without supervision and codes that perform exploratory data analysis will not be included.

## Analysis:

To clean the wiki_movie data, we started by filtering for only movies with "Director' and "Directed by" to reduce the lengthy columns. After this , we created a function for clean movies and passed a code to create an non destructive version and alternative titles of the movie data into it . We also created another function inside this main function to change the column nanes. After this , a function was created to take in the three [arguments](https://github.com/femolyn1/Movies_ETL/blob/b4ded04985db628cb536b8aa923619aec7d91119/Challenge.py#L85) and codes from the jupyter notebook were transferred into the function while the exploratory codes were left out.

### Assumptions:



