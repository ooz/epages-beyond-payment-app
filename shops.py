# -*- coding: utf-8 -*-

import psycopg2
import requests

class Shop(object):
    def __init__(self, id, hostname):
        self.id = id
        self.hostname = hostname

class Shops(object):
    def __init__(self):
        pass
    def get_shop(self, id):
        return None

class PostgresShops(Shops):
    def __init__(self, database_url):
        self.database_url = database_url

    def create_schema(self):
        with psycopg2.connect(self.database_url) as conn:
            with conn.cursor() as curs:
                curs.execute("""CREATE TABLE IF NOT EXISTS SHOPS (
                              ID varchar(255) UNIQUE NOT NULL,
                              HOSTNAME varchar(255) NOT NULL
                            )""")

    def create_or_update_shop(self, shop):
        print("Create/update shop %s (%s)" % (shop.hostname, shop.id))
        sql = ''
        if self.get_shop(shop.shop_id):
            sql = "UPDATE SHOPS SET HOSTNAME = %s WHERE ID=%s"
        else:
            sql = "INSERT INTO SHOPS (HOSTNAME, ID) VALUES(%s, %s)"
        with psycopg2.connect(self.database_url) as conn:
            with conn.cursor() as curs:
                curs.execute(sql, (shop.hostname, shop.id))

    def get_shop(self, id):
        with psycopg2.connect(self.database_url) as conn:
            with conn.cursor() as curs:
                curs.execute("SELECT * FROM SHOPS WHERE ID=%s", (id,))
                entry = curs.fetchone()
                if entry:
                    return Shop(id=entry[0],
                                hostname=entry[1])
        return None

def get_shop_id(installation):
    return \
        requests.get('%s/shop-id' % installation.api_url, \
                 headers={
                     "Accept": "application/hal+json",
                     "Authorization": "Bearer %s" % installation.access_token
                 }).json() \
        .get('shopId', None)
