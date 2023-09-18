import pandas as pd
import numpy as np

# Read books from csv file
df_books = pd.read_csv('./data/book.csv')

# Drop unecessary columns
df_books.drop(columns=['average_rating', 'isbn', 'ratings_count', 'text_reviews_count', 'publisher'], inplace=True)

# Rename columns for consistency
df_books.rename(columns={'isbn13':'isbn'}, inplace=True)

# Generate random total_copies for each book between 1 and 20
df_books['total_copies'] = np.random.randint(1, 21, df_books.shape[0])

# Generate random in_stock values such that 0 <= in_stock <= total_copies
df_books['in_stock'] = df_books['total_copies'] - np.random.randint(0, df_books['total_copies'] + 1)

# Save back to a csv file
df_books.to_csv('./data/book.csv', index=False)

