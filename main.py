from productclass import Product, Htmlextract ,CsvOperations,SqlOperations
from utils import field_names
import sqlite3

url ="/tshirts-men/pl/t3brl"
category = "Men"
sub_category="Top Wear"
child_category = "Tshirts"
csv_file_name = "files/products.csv"
no_of_pages_to_extract = 1 # default should be 1


cursor = None
table_name = 'products'
cat_table = 'cat_table'

# creating connection with database
try:
    sqliteConnection = sqlite3.connect('files/products.db')
    cursor = sqliteConnection.cursor()
    print("Database created and Successfully Connected to SQLite")

    sqlite_select_Query = "select sqlite_version();"
    cursor.execute(sqlite_select_Query)
    record = cursor.fetchall()
    print("SQLite Database Version is: ", record)

except sqlite3.Error as error:
    print("Error while connecting to sqlite", error)

if cursor:
    sql = SqlOperations(cursor,connection=sqliteConnection,table=table_name)
    sql_cat = SqlOperations(cursor,connection=sqliteConnection,table=cat_table)

    # create database
    sql_cat.create_table('cat')
    sql.create_table('product')



scraping_pages = sql_cat.get_unscrapped_data()
print(scraping_pages)

if not scraping_pages:
    print("No links of pages for scrapping")
    exit()

for page in scraping_pages:

    # page data: ('id' , 'link' , 'category' , 'sub_category' , 'child_category' ,'scrapped' )

    # getting links from given url
    for i in range(no_of_pages_to_extract):

        # hitting request
        product = Product(page[1])
        req = product.get_request(i+1)
        html_extract = Htmlextract(req)
        links = html_extract.get_on_page_product_links()

        # adding links to database scrapping from cat page
        for link in links:
            sql.insert_data({
                'link':link,
                'product_id':link.split('/')[-1],
                'scrapped':False,
                'category':page[2],
                'sub_category':page[3],
                'child_category':page[4]
            })
    
    sql_cat.update_data_by_id(page[0],{'scrapped':1})


# # start with adding all details of one product from database
not_scrapped_data = sql.get_unscrapped_data('id , link')


for i in not_scrapped_data:

    # comming data (id,link)

    url = i[1]
    product = Product(url)
    req = product.get_request()
    html_extract = Htmlextract(req)

    # json extracted
    html_extract.get_json()

    # details of one product
    details = html_extract.get_data_of_single_product()

    #  downloading image and getting path
    images =(html_extract.get_image_url(details['images']))
    details['images'] =images
    print(details)

    sql.update_data_by_id(i[0],details)


cursor.close()