import pandas as pd
import numpy as np
import random
from datetime import datetime

# Sample DataFrame for books
df_books = pd.read_csv('./data/book.csv', on_bad_lines='skip')

# Split the author strings into lists
df_books['author_list'] = df_books['authors'].str.split('/')

# Create a unique set of authors
unique_authors = set()
for authors in df_books['author_list']:
    unique_authors.update(authors)
unique_authors = list(unique_authors)

# Create a new authors DataFrame with unique author IDs
df_authors = pd.DataFrame({
    'id': range(1, len(unique_authors) + 1),
    'name': unique_authors
})

# Split name into first and last
df_authors['f_name'] = df_authors['name'].apply(lambda x: x.split(' ')[0].strip())
df_authors['l_name'] = df_authors['name'].apply(lambda x: ' '.join(x.split(' ')[1:]).strip())
df_authors.drop(columns='name', axis=1, inplace=True)

# Generate random dates of birth between 1900-2000 for each author
random_dates = []
for _ in range(len(df_authors)):
    year = random.randint(1900, 2000)
    month = random.randint(1, 12)
    day = random.randint(1, 28)  # To avoid issues with leap years and months with fewer than 31 days
    random_date = datetime(year, month, day)
    random_dates.append(random_date.strftime('%m/%d/%Y'))

df_authors['dob'] = random_dates

# Generate random nationalities for each author
nationalities = ['American', 'British', 'French', 'German', 'Chinese', 'South African', 'Indian', 'Native American', 'Thai', 'Canadian']
df_authors['nationality'] = np.random.choice(nationalities, len(df_authors))

# Create an author_book relationship DataFrame
author_book_list = []
for index, row in df_books.iterrows():
    book_id = row['bookID']
    for author in row['author_list']:
        author_id = df_authors[df_authors['name'] == author]['id'].iloc[0]
        author_book_list.append({'book_id': book_id, 'author_id': author_id})

df_author_book = pd.DataFrame(author_book_list)

# Drop the 'authors' and 'author_list' columns from df_books as they are no longer needed
df_books.drop(['authors', 'author_list'], axis=1, inplace=True)

# Show the DataFrames
print("Books DataFrame:")
print(df_books)
print("\nAuthors DataFrame:")
print(df_authors)
print("\nAuthor-Book Relationship DataFrame:")
print(df_author_book)

# Save the DataFrames to CSV files
df_books.to_csv('book.csv', index=False)
df_authors.to_csv('author.csv', index=False)
df_author_book.to_csv('author_book.csv', index=False)
