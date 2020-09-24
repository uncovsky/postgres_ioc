import requests
import psycopg2

def parse_ips(cursor):
    source = requests.get('https://www.badips.com/get/list/any/2')
    source = source.text

    with open("badips.txt", 'w+') as file:
        file.write(source)

        #copy downloaded data
        file.seek(0)
        cursor.execute('CREATE TABLE badips(id SERIAl PRIMARY KEY, ip_address cidr NOT NULL);')
        cursor.copy_expert("COPY badips(ip_address) FROM STDIN;", file)

        file.close()

def parse_data(cursor):
    #request data from given source
    response = requests.get("http://reputation.alienvault.com/reputation.data")

    #write bytes from the data file
    with open("reputation.data", "wb+") as file:
        file.write(response.content)
        file.seek(0)
        
        #create table
        cursor.execute('''CREATE TABLE alienvault
                        (id SERIAl PRIMARY KEY, 
                        ip_address cidr NOT NULL,
                        num1 INT NOT NULL,
                        num2 INT NOT NULL,
                        host text NOT NULL,
                        country_code VARCHAR(2) NOT NULL,
                        city text NOT NULL,
                        coordinates text NOT NULL,
                        num3 INT NOT NULL
                        );''')
        #insert data from file
        cursor.copy_expert('''COPY alienvault(ip_address, num1, num2, host, country_code, city, coordinates, num3)
        from STDIN (DELIMITER '#');''', file)
        


def parse_urls(cursor):

    #obtain data
    response = requests.get("https://openphish.com/feed.txt")
    response = response.text

    with open("urls.txt", "w+") as file:
        file.write(response)

        #reading from file to get around SQL COPY issues (we delimiters in urls)
        file.seek(0)
        url_list = file.readlines()
        url_list = [line.strip() for line in url_list]

        #new table for data, includes domain names and others for easier queries
        cursor.execute('''CREATE TABLE openphish
                        (id SERIAl PRIMARY KEY, 
                        url text NOT NULL,
                        scheme text DEFAULT ' ' NOT NULL,
                        domain text DEFAULT ' ' NOT NULL,
                        path text DEFAULT ' ' NOT NULL
                        );''')

        #copy raw urls from file
        file.seek(0)
        cursor.copy_expert("COPY openphish(url) FROM STDIN;", file)            
        id = 1
        for url in url_list:
            split_url = url.split('/')
            path = ('/'.join(split_url[3:]))
            cursor.execute("UPDATE openphish SET scheme = %s, domain = %s, path = %s WHERE id = %s", (split_url[0][:-1], split_url[2], path, id))
            id+=1

        file.close()
