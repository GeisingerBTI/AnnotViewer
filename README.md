# cTakes Annotation Viewer

1. Clone the repository 
2. Create config.py under instance/ folder
    - Add config.py and define the following:
        1. DATABASE_CONNECTION: This is the connection to get teh XMI on a database server
        2. SQLALCHEMY_DATABASE_URI: This is the connection used to store the user information for access
        3. SECRET_KEY: Should be a randomly generated string used for securing sessions
        4. LDAP_URI: LDAP connection string
        5. DOMAIN_NAME: This is used for LDAP authentication so you can bind without performing a search
3. Update config.py under root directory.  This holds not secure configuration parameters
    1. DEBUG: True or False
    2. TABLE_NAME: Specifies the table name where the user information will be stored
    3. PERMANENT_SESSION_LIFETIME: Specify in number of seconds for how long a session should last before expiring
    4. TIMEOUT_WARNING_MS: Time in milliseconds until a warning should pop up to user that session will expire
    5. TIMEOUT_LOGOUT_MS: Time in milliseconds until the user is logged out
    6. KEEPALIVE_INTERVAL_MS: Time in milliseconds that a ping will occur to keep the session alive on backend
    7. SITE_NAME: The name of the header for the site you want to use
4. If deploying to Apache/NGINX create WSGI deployment configs as apppropriate or run runserver.py