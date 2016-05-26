#!/usr/bin/env python

__author__ = "Brandon Geise"
__copyright__ = "Copyright 2016, Geisinger Health System"
__license__ = "Apache 2.0"

from AnnotViewer import app
try:
    import ldap
except:
    pass


def get_ldap_connection():
    ldap.set_option(ldap.OPT_X_TLS_REQUIRE_CERT, ldap.OPT_X_TLS_NEVER)
    conn = ldap.initialize(app.config["LDAP_URI"])
    conn.set_option(ldap.OPT_REFERRALS, 0)
    conn.set_option(ldap.OPT_PROTOCOL_VERSION, 3)
    conn.set_option(ldap.OPT_X_TLS,ldap.OPT_X_TLS_DEMAND)
    conn.set_option( ldap.OPT_X_TLS_DEMAND, True )
    conn.set_option( ldap.OPT_DEBUG_LEVEL, 255 )
    return conn

def ldapLogin(username,password):
    conn = get_ldap_connection()
    try:
        conn.simple_bind_s(username + app.config['DOMAIN_NAME'],password)
        return True
    except ldap.INVALID_CREDENTIALS:
        return False