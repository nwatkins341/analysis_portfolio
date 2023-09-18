import pandas as pd
import numpy as np

# Getting unique book ids for the transaction table
df = pd.read_csv('./data/book.csv', on_bad_lines='skip')

ids = df.bookID.to_list()
print(ids)  # I used these values as a custom list for Mockaroo

# Read the CSV file into a Pandas DataFrame
df = pd.read_csv('./data/transaction.csv')

# Convert date columns to datetime dtype
df['date_borrow'] = pd.to_datetime(df['date_borrow'])

# Generate date_due by adding 3 to 12 weeks to date_borrow
df['date_due'] = df['date_borrow'] + pd.to_timedelta(
    np.random.randint(3, 13, size=len(df)) * 7, unit='D')

# Initialize an empty column for date_return
df['date_return'] = np.nan

# Generate date_return for 95% of the rows
mask_95 = np.random.rand(len(df)) < 0.95
df.loc[mask_95, 'date_return'] = df.loc[mask_95, 'date_borrow'] + pd.to_timedelta(
    np.random.randint(0, (df.loc[mask_95, 'date_due'] - df.loc[mask_95, 'date_borrow']).dt.days), unit='D')

# For the remaining 5%, either leave it as NaN or set it to a date after date_due
mask_5 = ~mask_95
mask_5_late = np.random.rand(len(df[mask_5])) < 0.5

df.loc[mask_5, 'date_return'] = df.loc[mask_5, 'date_due'] + pd.to_timedelta(
    np.random.randint(1, 31), unit='D') * mask_5_late

# Remove timestamp from date_return
df['date_return'] = df['date_return'].str.split(" ").str[0]

# Convert date columns to datetime dtype
df['date_due'] = pd.to_datetime(df['date_due'])
df['date_return'] = pd.to_datetime(df['date_return'], errors='coerce')  # This will convert 'Not Returned' and other invalid entries to NaT (Not a Time)

# Initialize a new 'fee' column with zeros
df['fee'] = 0.0

# Calculate the days overdue for each row
df['days_overdue'] = (df['date_return'] - df['date_due']).dt.days

# Calculate the fee for rows where the book was returned late
df.loc[df['days_overdue'] > 0, 'fee'] = df['days_overdue'] * 0.10

# Calculate the fee for rows where the book has not been returned and the due date is before 9/15/23
today = pd.Timestamp('2023-09-15')
df.loc[df['date_return'].isna() & (df['date_due'] < today), 'fee'] = (today - df['date_due']).dt.days * 0.10

# Drop the 'days_overdue' column as it was only needed for the calculation
df.drop('days_overdue', axis=1, inplace=True)

# Replace zeros in the 'fee' column with NaN
df.loc[df['fee'] == 0, 'fee'] = np.nan

# Round the 'fee' column to two decimal places
df['fee'] = df['fee'].round(2)

# Convert 'fee' to string format, keeping two decimal places
df['fee'] = df['fee'].apply(lambda x: '{:.2f}'.format(x) if pd.notna(x) else x)

# Save the modified DataFrame back to CSV
df.to_csv('transaction.csv', index=False)
