import arrow
from sqlalchemy import Column, Integer, String, Float
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

import helpers
import myconfigurations as config
from pycarousell import CarousellSearch

Base = declarative_base()

class CarousellListing(Base):
    __tablename__ = 'itemlistings'
    id = Column(Integer, primary_key=True)
    listing_id = Column(Integer)
    seller = Column(String)
    title = Column(String)
    currency_symbol = Column(String)
    price = Column(Float)
    time = Column(String)

engine = create_engine('sqlite:///searchListings.db')
Base.metadata.create_all(engine)
Session = sessionmaker(bind=engine)
session = Session()

def find_stuff(index, search_query):
    my_want = CarousellSearch(search_query, results=config.RESULTS_COUNT)
    try:
        results = my_want.send_request()
    except Exception as e:
        results = []
        robot.post_message(helpers.multiplyEmoji(":x:", 3) + "ERROR IN API REQUEST: %s" % e)

    count = 0
    line_item = ""
    for r in results:
        count += 1
        print("{}) {}".format(str(count), r))
        #skip results without query in listing title OR description
        want = search_query.lower()
        itemPrice = float(r['price'])
        minPrice = config.PRICE_MINIMUM[index]
        maxPrice = config.PRICE_MAXIMUM[index]
        targetPrice = config.PRICE_TARGET[index]
        productImage = r['primary_photo_url']

        if want not in (r['title']).lower() and want not in (r['description']).lower():
            print("Out of search. Skip! " + (r['title']))
            continue

        # Check if item is within specified price range
        if itemPrice <= minPrice or itemPrice >= maxPrice:
            print("Price out of range. Ignore!")
            continue

        # Ignore items with unwanted keywords
        if any([ign in r['title'].lower() for ign in config.IGNORES]) or any([ign in r['description'].lower() for ign in config.IGNORES]):
            print("Item ignored!")
            continue

        #check if listing is in DB already
        check = (session.query(CarousellListing).filter_by(listing_id=r['id']).
                    first())


        # Details of item
        item_details = r['seller']['username'] + "(https://sg.carousell.com/" + r['seller']['username'] + ")\n" + \
                     r['title'] + \
                     "\n:heavy_dollar_sign:" + r['price'] + "\n" + \
                     arrow.get(r['time_indexed']).format('DD/MM/YYYY HH:MM') + "\n"

        #if it is not in DB
        if check is None:
            line_item = item_details

            # Add highlight when target price is met
            if itemPrice <= targetPrice:
                line_item += helpers.multiplyEmoji(":heavy_dollar_sign:", 8)

            line_item += "\n\n"

            helpers.postMessage(line_item, productImage)

            listing = CarousellListing(
                listing_id = r['id'],
                seller = r['seller']['username'],
                title = r['title'],
                currency_symbol = r['currency_symbol'],
                price = r['price'],
                time = arrow.get(r['time_created']).format('DD/MM/YYYY HH:MM')
            )
            session.add(listing)
            session.commit()

        else:
            print("Item checked before!")
            if check is not None:
                if itemPrice < float(check.price):
                    line_item = item_details
                    line_item += helpers.multiplyEmoji(":exclamation:", 3) + "ITEM PRICE HAS BEEN REDUCED" + \
                                 helpers.multiplyEmoji(":exclamation:", 3) + "\n Old price::heavy_dollar_sign:" + '%.2f' % check.price
                    line_item += "\n\n"

                    helpers.postMessage(line_item)

                    check.price = itemPrice
                    session.commit()

    return
