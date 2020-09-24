#!/usr/bin/env python3
import psycopg2
import data
import requests


if __name__ == "__main__":

    #connect to the default database
    connection = psycopg2.connect('dbname=postgres user=postgres password=postgres')
    cursor = connection.cursor()

    #parse data from given sources
    data.parse_urls(cursor)


    #commit and terminate connection, end result is 3 tables from respective data sources
    connection.commit()
    cursor.close()
    connection.close()
    



   