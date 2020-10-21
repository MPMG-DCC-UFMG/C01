# PostgreSQL settings (needed to access saved statistics from previous crawls)
POSTGRESQL_USER = 'postgres'
POSTGRESQL_PASSWORD = 'my_password'
POSTGRESQL_HOST = 'localhost'
POSTGRESQL_PORT = 5432

# Name of the database that saved the crawl metadata.
CRAWL_HISTORIC_DB_NAME = 'auto_scheduler'

# Name of the table where crawl history is saved.
CRAWL_HISTORIC_TABLE_NAME = 'CRAWL_HISTORIC'

# Name of the column where the crawl history is.
# (Yes, by default, the column and table name where the history is saved are the same.)
CRAWL_HISTORIC_COLUMN_NAME = 'CRAWL_HISTORIC'
