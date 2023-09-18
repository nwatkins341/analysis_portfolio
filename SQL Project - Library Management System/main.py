# Import statements
import sqlite3
import pandas as pd

# Setting up connection
conn = sqlite3.connect('library.db')
c = conn.cursor()

# Creating initial tables
c.execute('''CREATE TABLE IF NOT EXISTS book
    (id INTEGER PRIMARY KEY AUTOINCREMENT,
    title TEXT NOT NULL,
    isbn VARCHAR(17) UNIQUE,
    language_code CHAR(3),
    num_pages SMALLINT,
    pub_year CHAR(4),
    in_stock SMALLINT,
    total_copies SMALLINT);''')

c.execute('''CREATE TABLE IF NOT EXISTS "transaction"
    (id INTEGER PRIMARY KEY AUTOINCREMENT,
    book_id INTEGER REFERENCES book(id),
    borrower_id INTEGER REFERENCES borrower(id),
    date_borrow DATE,
    date_due DATE,
    date_return DATE,
    fee NUMERIC(5, 2));''')

c.execute('''CREATE TABLE IF NOT EXISTS borrower
    (id INTEGER PRIMARY KEY AUTOINCREMENT,
    f_name VARCHAR(64) NOT NULL,
    l_name VARCHAR(64) NOT NULL,
    gender CHAR(1),
    email VARCHAR(128) UNIQUE,
    phone VARCHAR(25) CHECK (phone GLOB '[0-9]*'),
    mem_date DATE,
    exp_date DATE);''')

c.execute('''CREATE TABLE IF NOT EXISTS author
    (id INTEGER PRIMARY KEY AUTOINCREMENT,
    f_name VARCHAR(64) NOT NULL,
    l_name VARCHAR(64),
    dob DATE,
    nationality VARCHAR(32));''')

c.execute('''CREATE TABLE IF NOT EXISTS author_book
    (id INTEGER PRIMARY KEY AUTOINCREMENT,
    book_id INTEGER REFERENCES book(id),
    author_id INTEGER REFERENCES author(id));''')

conn.commit()

# Loading data from CSV files into DataFrames
df_book = pd.read_csv('./data/book.csv')
df_author = pd.read_csv('./data/author.csv')
df_author_book = pd.read_csv('./data/author_book.csv')
df_transaction = pd.read_csv('./data/transaction.csv')
df_borrower = pd.read_csv('./data/borrower.csv')

# Inserting data from DataFrames into SQLite tables
df_book.to_sql('book', conn, if_exists='append', index=False)
df_author.to_sql('author', conn, if_exists='append', index=False)
df_author_book.to_sql('author_book', conn, if_exists='append', index=False)
df_transaction.to_sql('transaction', conn, if_exists='append', index=False)
df_borrower.to_sql('borrower', conn, if_exists='append', index=False)

# Standardizing English language code
c.execute('''
UPDATE book
SET language_code = "eng"
WHERE language_code = "en-GB"
OR language_code = "en-US"
OR language_code = "en-CA"
''')

conn.commit()

# SQL Queries

# Question 1: What book or books are taken out most often?
q1 = pd.read_sql_query('''
SELECT book.title, COUNT("transaction".id) as transaction_count
FROM "transaction"
JOIN book ON book.id = "transaction".book_id
GROUP BY "transaction".book_id, book.title
HAVING transaction_count = (
    SELECT MAX(transaction_count) FROM (
        SELECT COUNT(id) as transaction_count
        FROM "transaction"
        GROUP BY book_id
    )
)
ORDER BY transaction_count DESC;
''', conn)

'''
         title  transaction_count
0  The Shining                  4
'''


# Question 2: What are the top 5 (by count) non-English language codes in the book table?
q2 = pd.read_sql_query('''
SELECT language_code, COUNT(*) as book_count
FROM book
WHERE language_code != "eng"
GROUP BY language_code
ORDER BY COUNT(*) DESC
LIMIT 5;
''', conn)

'''
  language_code  book_count
0           spa         218
1           fre         144
2           ger          99
3           jpn          46
4           mul          19
'''


# Question 3: Which borrowers have overdue books?
q3 = pd.read_sql_query('''
SELECT borrower.f_name || ' ' || borrower.l_name as full_name,
COUNT("transaction".id) as overdue_books
FROM borrower
JOIN "transaction" ON borrower.id = "transaction".borrower_id
WHERE "transaction".date_due < date('now')
AND "transaction".date_return IS NULL
GROUP BY full_name
ORDER BY borrower.l_name;
''', conn)

'''
              full_name  overdue_books
0           Heath Acton              1
1              Ado Adie              1
2      Marmaduke Adshed              1
3            Fern Agass              1
4    Alverta Androletti              1
..                  ...            ...
106      Stuart Tyhurst              1
107        Lynne Wegner              1
108   Davina Wiggington              1
109     Karna Willmetts              1
110         Deana Worcs              1
'''


# Question 4: How much money is the library owed in fees?
q4 = pd.read_sql_query('''
SELECT SUM(fee) as total_fees
FROM "transaction"
WHERE fee IS NOT NULL
''', conn)

'''
   total_fees
0      1935.0
'''


# Question 5: What is the breakdown of books borrowed per month?
q5 = pd.read_sql_query('''
SELECT strftime('%m', date_borrow) as month, COUNT(*) as total_borrowed
FROM "transaction"
GROUP BY strftime('%m', date_borrow);
''', conn)

'''
   month  total_borrowed
0     01             247
1     02             234
2     03             266
3     04             260
4     05             256
5     06             235
6     07             251
7     08             254
8     09             230
9     10             259
10    11             238
11    12             261
'''


# Question 6: What percentage of borrowers borrow more than once?
q6 = pd.read_sql_query('''
SELECT (
    COUNT(borrower_id) * 100 / (
        SELECT COUNT(*) FROM borrower
        )
    )
FROM (
    SELECT borrower_id
    FROM "transaction"
    GROUP BY borrower_id
    HAVING COUNT(*) > 1
    );
''', conn)

# Answer: 79%


# Question 7: Who are the top 10 most popular authors in the dataset?
q7 = pd.read_sql_query('''
SELECT author.f_name || ' ' || author.l_name AS author_name,
COUNT("transaction".id) AS transaction_count
FROM "transaction"
JOIN book ON "transaction".book_id = book.id
JOIN author_book ON book.id = author_book.book_id
JOIN author ON author_book.author_id = author.id
GROUP BY author.id, author_name
ORDER BY transaction_count DESC
LIMIT 10;
''', conn)

'''
            author_name  transaction_count
0          Stephen King                 42
1   William Shakespeare                 30
2        J.R.R. Tolkien                 19
3           Dean Koontz                 15
4       Agatha Christie                 15
5            Roald Dahl                 14
6     Kurt Vonnegut Jr.                 13
7        Hirohiko Araki                 13
8  Edgar Rice Burroughs                 13
9   Friedrich Nietzsche                 13
'''


# Question 8: What is the breakdown of books with more than 1 author?
q8 = pd.read_sql_query('''
SELECT num_authors, COUNT(*) as num_books
FROM (
    SELECT book_id, COUNT(author_id) as num_authors
    FROM author_book
    GROUP BY book_id
) AS subquery
WHERE num_authors > 1
GROUP BY num_authors
ORDER BY num_authors;
''', conn)

'''
    num_authors  num_books
0             2       3079
1             3       1005
2             4        222
3             5         65
4             6         54
5             7         21
6             8         11
7             9         10
8            10         12
9            11          9
10           12          5
11           13          8
12           14          1
13           15         11
14           16          6
15           17          6
16           18          8
17           19          4
18           20          3
19           21          8
20           22          1
21           23          2
22           24          3
23           25          1
24           26          1
25           27          1
26           28          1
27           32          1
28           33          1
29           35          1
30           38          1
31           51          1
'''


# Question 8.5: What book has 51 authors???
q85 = pd.read_sql_query('''
SELECT book.id, book.title
FROM book
WHERE book.id IN (
    SELECT book_id
    FROM author_book
    GROUP BY book_id
    HAVING COUNT(author_id) = 51
);
''', conn)

'''
      id                      title
0  39690  Good Poems for Hard Times

A poetry anthology! That makes sense.
'''


# Question 9: What is the average number of days it takes to return a book?
q9 = pd.read_sql_query('''
SELECT AVG(julianday(date_return) - julianday(date_borrow)) 
FROM "transaction" 
WHERE date_return IS NOT NULL;
''', conn)

# Answer: 27.5 days


# Question 10: Which books are checked out and returned on the same day (potentially indicating they are being used as reference books)?
q10 = pd.read_sql_query('''
SELECT book.title, 
AVG(julianday("transaction".date_return) - julianday("transaction".date_borrow)) as avg_days_borrowed
FROM book
INNER JOIN "transaction" ON book.id = "transaction".book_id
WHERE "transaction".date_return IS NOT NULL
GROUP BY book.id, book.title
HAVING COUNT("transaction".id) > 0 AND avg_days_borrowed = 0
ORDER BY avg_days_borrowed ASC;
''', conn)

'''
                                                title  avg_days_borrowed
0                             Henry Miller on Writing                0.0
1                                   Bleach  Volume 14                0.0
2                                Kiffe Kiffe Tomorrow                0.0
3                    The Mysteries of Sherlock Holmes                0.0
4                           Theater Shoes (Shoes  #4)                0.0
5   The Road Less Traveled: A New Psychology of Lo...                0.0
6                                    An Ideal Husband                0.0
7                                             Ivanhoe                0.0
8                           Easy Riders  Raging Bulls                0.0
9                The Andromeda Strain (Andromeda  #1)                0.0
10                                 Ballet for Dummies                0.0
11                              The Elephant Vanishes                0.0
12                                   The Tenth Circle                0.0
13                                   My Year of Meats                0.0
14                                       Tuf Voyaging                0.0
15           Storm Rising (Valdemar: Mage Storms  #2)                0.0
16                                 The Hermit's Story                0.0
17  The Day the Country Died: A History of Anarcho...                0.0
18  Black on Red: My 44 Years Inside the Soviet Un...                0.0
19                                   Nineteen Minutes                0.0
20  The Finer Points of Sausage Dogs (Portuguese I...                0.0
21                           The Assignation: Stories                0.0
22                                   Romeo and Juliet                0.0
23                         Shake Hands with the Devil                0.0
24                      The Real Trial of Oscar Wilde                0.0
25                 Hundred-Dollar Baby (Spenser  #34)                0.0
26                    Beyond Reach (Grant County  #6)                0.0
27  Imperial Life in the Emerald City: Inside Iraq...                0.0
28  The Origins of the Civil Rights Movements: Bla...                0.0
29                  Flow My Tears  the Policeman Said                0.0
30                            Secrets of the Scorpion                0.0
31                Eugene Onegin  Vol. II (Commentary)                0.0
32  The Daring Young Man on the Flying Trapeze and...                0.0
33               Twisted: The Collected Short Stories                0.0
34                                         Wind Child                0.0
35      Happy Are the Peace Makers (Blackie Ryan  #5)                0.0
36   Cerulean Sins (Anita Blake  Vampire Hunter  #11)                0.0
37                             Philosophy for Dummies                0.0
38                               Summer of the Dragon                0.0
39                                       The Wanderer                0.0
40                   The Last Story (Remember Me  #3)                0.0
41                                   Proof of Concept                0.0
42  A People's Tragedy: The Russian Revolution: 18...                0.0
43                                    The Fish Kisser                0.0
44  Lord John and the Brotherhood of the Blade  (L...                0.0
45  Masters of Enterprise: Giants of American Busi...                0.0
46                      Asimov's New Guide to Science                0.0
47         The Stars  Like Dust (Galactic Empire  #1)                0.0
'''

conn.close()

