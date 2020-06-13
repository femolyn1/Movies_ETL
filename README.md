# Movies_ETL

The purpose of this project is to write a script to extract, transform and load the provided data.  This script will be automated to carry out the ETL proces without supervision and codes that perform exploratory data analysis will not be included.

## Analysis:

To clean the wiki_movie data, we started by filtering for only movies with "Director' and "Directed by" to reduce the lengthy columns. After this , we created a function for clean movies and passed a code to create an non destructive version and alternative titles of the movie data into it . We also created another function inside this main function to change the column nanes. After this , a function was created to take in the three [arguments](https://github.com/femolyn1/Movies_ETL/blob/b4ded04985db628cb536b8aa923619aec7d91119/Challenge.py#L85) and codes from the jupyter notebook were transferred into the function while the exploratory codes were left out.

### Assumptions:

The following assumptions were made while writing this script:

 * While extracting the IMDB from the IMDb link, the system might throw an error is the data contains no [IMDB_link](https://github.com/femolyn1/Movies_ETL/blob/3e51935981002dad536908f6aeec1c20dcf8bc7b/Challenge.py#L104). To mitigate this , a try, except statement was added. 
 
 * Some kaggle data with non numeric data type like the ['Id'](https://github.com/femolyn1/Movies_ETL/blob/2346079aea05dce8a316646373d0339fa4b99f07/Challenge.py#L229) and 'popularity' columns  might be convertible to numbers. To mitigate this, errors was set to raise within those codes. 
 
 * [Adult column](https://github.com/femolyn1/Movies_ETL/blob/9e42f51e56607cd7fa5057079c178308b3865e3d/Challenge.py#L222) in the kaggle data is too messy and will be dropped.
 
 * Some movies will have no [rating](https://github.com/femolyn1/Movies_ETL/blob/edd43113f23f35790b5356c03ed0a82d4b3ff08a/Challenge.py#L307) information hence we will fill with zeros.
 
 * Error might occur while loading into SQL, hence a try except statement was added.
 
 ## Summary: 
 
 Although this script can be further revamped for better performance, it provides insight into the effectiveness of the ETL automation process. Companies are currently leveraging this process to reduce rework and boost efficiency.





