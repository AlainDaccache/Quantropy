from datetime import datetime
import pymongo

# make sure you disable firewall (either Windows Defender Firewall or third-party service i.e. McAfee)
myclient = pymongo.MongoClient("mongodb://localhost:27017/")
mydb = myclient["MATILDA"]
# create collection (not technically created until record inserted)
financial_statements_collection = mydb["Financial Statements"]
financial_statements_document = {"filing_date": datetime(2019, 1, 1),
                                 "stock_ticker": 'AAPL',
                                 "filing_type": '10-K',
                                 "balance sheet": {},
                                 "income statement": {},
                                 "cash flow statement": {}}

# x = financial_statements_collection.insert_one(financial_statements_document)  # insert one record in collection
# print(x.inserted_id)  # mongoDB assigns unique id (by default)
print(mydb['Financial Statements'].find_one())
#
# mylist = [{"_id": 1, "name": "Amy", "address": "Apple st 652"},
#           {"_id": 2, "name": "Hannah", "address": "Mountain 21"}]
# x = mycol.insert_many(mylist)  # insert many records in collection
# print(x.inserted_ids)  # you can specify ids with '_id' field
#
# x = mycol.find_one()  # find first document in collection
#
# for x in mycol.find():  # can iterate over documents in collection
#     print(x)
#
# '''The first argument of the find() method is a query object, and is used to limit the search.
# When finding documents in a collection, you can filter the result by using a query object.'''
# mydoc = mycol.find({"address": "Park Lane 38"})
# # Find documents where the address starts with the letter "S" or higher:
# mydoc = mycol.find({"address": {"$gt": "S"}})
# # Find documents where the address starts with the letter "S":
# mydoc = mycol.find({"address": {"$regex": "^S"}})
#
# '''The second argument of the find() method helps you specify which fields to include in result (by default, all): 0 for don't, and 1 for do.
# NB: You are not allowed to specify both 0 and 1 values in the same object (except if one of the fields is the _id field).
# If you specify a field with the value 0, all other fields get the value 1, and vice versa:'''
# for x in mycol.find({}, {"_id": 0, "name": 1, "address": 1}):
#     print(x)
#
# # Sort the result alphabetically by name (1 for ascending, -1 for descending), 1 by default
# mydoc = mycol.find().sort("name", -1)
#
# # Delete the document with the address "Mountain 21" (if many, will only delete first occurence)
# mycol.delete_one({ "address": "Mountain 21" })
#
# # Delete all documents were the address starts with the letter S
# mycol.delete_many({ "address": {"$regex": "^S"} })
#
# # Delete all documents in the collection:
# mycol.delete_many({})
#
# # Delete the collection
# mycol.drop()
#
