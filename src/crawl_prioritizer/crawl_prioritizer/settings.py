# Change the priority equation using the variables:
#    - domain_prio: Priority of the crawl domain. If it is not defined in the DOMAIN_PRIORITY dictionary, by default, it will be 1. 
#    - time_since_last_crawl: Time in seconds since the last crawl. If this value is not available, it will be the largest possible (obtained by sys.maxsize).
#    - change_frequency: Update frequency estimated in seconds. 
# 
# Use only math functions from the math library in your equation and "crawl_priority" MUST appear on the left side of the equality.
#
# Arbitrary equation for demonstration ONLY.
PRIORITY_EQUATION = 'crawl_priority = domain_prio + math.log(time_since_last_crawl) + 1 / change_frequency'

# Upper and lower limits for the priority of a crawl.
MAX_PRIORITY = 100
MIN_PRIORITY = 0

# Priority of never made crawls
PRIORITY_NEVER_MADE_CRAWL = 87

# By default, every domain has priority 1. Change the priority for domains in this dictionary.
DOMAIN_PRIORITY = {
    'some_url.com': 81
}

# PostgreSQL settings (needed to access saved statistics from previous crawls, 
# changing the time_since_last_crawl and change_frequency variables values automatically.)
POSTGRESQL_USER = 'postgres'
POSTGRESQL_PASSWORD = 'my_password'
POSTGRESQL_HOST = 'localhost'
POSTGRESQL_PORT = 5432