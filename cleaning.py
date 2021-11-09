import pandas as pd
import numpy as np
import re
import math
import geopandas as gpd
from shapely.geometry import Point, Polygon
import matplotlib.pyplot as plt
import seaborn as sns
import matplotlib.pyplot as plt
import math

def df_clean(df):
    #reset_index
    df.reset_index(inplace=True)


    #turn price into int
    #df["price"] = df["price"].str.replace(",","")
    #df["price"] = df["price"].str.replace("$","")
    #df["price"] = df["price"].astype("int")

    
    #drop duplicate rows on URL
    df = df.drop_duplicates("url")
    
    #reset_index\n",
    df.reset_index(inplace=True)
   
    #turn price into int
    df["price"] = df["price"][df["price"].notnull()].str.replace(",","")
    df["price"] = df["price"][df["price"].notnull()].str.replace("$","")
    df["price"] = df["price"][df["price"].notnull()].astype("int")
    
    #shipping price
    df["shipping_price"] = df["shipping_price"][df["shipping_price"].notnull()].apply(lambda x: x.split(" ")[1])
    df["shipping_price"] = df["shipping_price"][df["shipping_price"].notnull()].apply(lambda x: x.replace("Shipping", "0")
                                                                                      .replace("$","")
                                                                                      .replace(".",""))
                                                                                     
    df["shipping_price"] = df["shipping_price"][df["shipping_price"].notnull()].replace('Local', np.nan)
    df["shipping_price"] = df["shipping_price"][df["shipping_price"].notnull()].apply(lambda x: float(x)/100)



    #category

    df["category"] = df["category"][df["category"].notnull()].apply(lambda x: x
                                                                    .replace("[","")
                                                                    .replace("]","")
                                                                    .replace("'","")
                                                                    .replace("\\",""))
    df["category"] = df["category"][df["category"].notnull()].apply(lambda x: x.split(", "))
   
    #buld category tiers
    df["cat_length_of_1"] = df["category"][df["category"].notnull()].apply(lambda x: len(x)>=2)
    df["cat_length_of_2"] = df["category"][df["category"].notnull()].apply(lambda x: len(x)>=3)
    df["cat_length_of_3"] = df["category"][df["category"].notnull()].apply(lambda x: len(x)>=4)
    df["cat_length_of_4"] = df["category"][df["category"].notnull()].apply(lambda x: len(x)>=5)
    df["cat_length_of_5"] = df["category"][df["category"].notnull()].apply(lambda x: len(x)>=6)

    df["category_1"] = df["category"][df["category"].notnull()].apply(lambda x: x[0] if x[0]!="" else np.nan)

    #df["shipping_price"] = df["shipping_price"].apply(lambda x: int(x.replace("$","")
    #                                                                .replace(".","")
    #                                                                .split(" ")[1])/100 if x!="Free Shipping" else 0)


    #category
#     df["category"] = df["category"][df["category"].notnull()].apply(lambda x: x
#                                                                     .replace("[","")
#                                                                     .replace("]","")
#                                                                     .replace("'","")
#                                                                     .replace("\\",""))
                                                                             
#     df["category"] = df["category"][df["category"].notnull()].apply(lambda x: x.split(", "))
                                                                                                                                        
    #build category tiers
    df["cat_length_of_1"] = df["category"][df["category"].notnull()].apply(lambda x: len(x)>=2)
    df["cat_length_of_2"] = df["category"][df["category"].notnull()].apply(lambda x: len(x)>=3)
    df["cat_length_of_3"] = df["category"][df["category"].notnull()].apply(lambda x: len(x)>=4)
    df["cat_length_of_4"] = df["category"][df["category"].notnull()].apply(lambda x: len(x)>=5)
    df["cat_length_of_5"] = df["category"][df["category"].notnull()].apply(lambda x: len(x)>=6)


    df["category_1"] = df["category"][df["category"].notnull()].apply(lambda x: x[0] if x[0]!="" else np.nan)

    #df["category_1"] = df["category"].apply(lambda x: x[0] if x[0]!="" else np.nan)

    df["category_2"] = df[df["cat_length_of_1"]==True]["category"].apply(lambda x: x[1])
    df["category_3"] = df[df["cat_length_of_2"]==True]["category"].apply(lambda x: x[2])
    df["category_4"] = df[df["cat_length_of_3"]==True]["category"].apply(lambda x: x[3])
    df["category_5"] = df[df["cat_length_of_4"]==True]["category"].apply(lambda x: x[4])
    df["category_6"] = df[df["cat_length_of_5"]==True]["category"].apply(lambda x: x[5])

    df.drop(columns=["cat_length_of_1","cat_length_of_2","cat_length_of_3","cat_length_of_4","cat_length_of_5"],axis=1, inplace=True)
    
    #clean up original price
    df["original_price"] = df["original_price"].apply(lambda x: np.nan if type(x)==np.float else int(x.replace("$","").replace(",","")))

    #clean up sold status and turn into binary


    #clean up sold status and turn into binary
    df["sold_status"] = df["sold_status"].apply(lambda x: "Sold" if x=="Item sold" else "Not Sold")
    df["sold_status"] = df["sold_status"].apply(lambda x: 0 if x=="Not Sold" else 1)
                                                                                                                                        
    #location
    df["location"] = df["location"][df["location"].notnull()].apply(lambda x: x
                                                                    .replace("['Local | $10.99']","")
                                                                    .replace("[]","")
                                                                    .split("|")[-1]
                                                                    .replace("from","")
                                                                    .replace("']","")
                                                                    .strip())
    
    df["location"] = df["location"].replace("", np.nan)

    #clean up sold status

    df["sold_status"] = df["sold_status"].apply(lambda x: "Sold" if x=="Item sold" else "Not Sold")
    df["sold_status"] = df["sold_status"].apply(lambda x: 0 if x=="Not Sold" else 1)
    

    #User_Id
    df["user_id"] = df["user_id"][df["user_id"].notnull()].apply(lambda x: x.replace("Sold by ",""))
    
    #profile verified
    df["profile_verified"] = df["profile_verified"][df["profile_verified"].notnull()].apply(lambda x: x.split(",")[-1]
                                                                                            .replace("'","")
                                                                                            .replace("]","")
                                                                                            .replace("sales","Not Verified")
                                                                                            .replace("sale","Not Verified").strip())
    
    #badges
    df["badges"] = df["badges"][df["badges"].notnull()].apply(lambda x: list(set(re.findall("badge_(.+?).svg", x))))
    
    df["reliable"] = df["badges"][df["badges"].notnull()].apply(lambda x: 1 if "reliable" in x else 0)
    df["speedy_shipper"] = df["badges"][df["badges"].notnull()].apply(lambda x: 1 if "speedy_shipping" in x else 0)
    df["fast_response"] = df["badges"][df["badges"].notnull()].apply(lambda x: 1 if "fast_response" in x else 0)
    df["member_since"] = df["badges"][df["badges"].notnull()].apply(lambda x: int("".join(re.findall("\d","".join(x)))))
    
    #responsiveness
    df["response_within_24hours"] = df["responsive"][df["responsive"].notnull()].apply(lambda x: 1 if x=="This seller usually responds within 24 hours" else 0)
    
                                                                                                                                        
    #discount

    df["discount"] = abs((df["price"] - df["original_price"])/df["original_price"])*100
    df["discount"] = df["discount"].replace(np.nan, 0)
    
    #convert posted date to datetime object
    df["posted_date"] = pd.to_datetime(df["posted_date"])
    
    #profile verified - convert to binary
    df["profile_verified"] = df["profile_verified"][df["profile_verified"].notnull()].apply(lambda x: 1 if x=="Profile verified" else 0 )

    df["profile_verified"] = df["profile_verified"].apply(lambda x: 1 if x=="Profile verified" else 0 )

    
    
    #drop duplicate rows on URL
    #df = df.drop_duplicates("url")


    return df



