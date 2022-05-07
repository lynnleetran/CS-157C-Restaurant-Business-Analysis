from audioop import add
import os
import pymongo
import json
import io
import re
import datetime
from pymongo import MongoClient
from bson.objectid import ObjectId
from bson.son import SON

HOST_IP = "18.207.247.141"
HOST_PORT = "27017"

def main():

    uri = "mongodb://"+HOST_IP+":"+HOST_PORT

    client = MongoClient(uri)
    print("Connected to",HOST_IP+":"+HOST_PORT+" successfully!")
    db = client["testdb"]
    businessCollection = db["businessCollection"]
    reviewCollection = db["reviewCollection"]
    userCollection = db["userCollection"]
    tipCollection = db["tipCollection"]

    while True:
        print("Welcome to the YELP Business Analysis Tool")
        print("Choose an option from the following: ")
        print("1. Find top 10 restaurants in location X")
        print("2. List of users who provide the most number of compliments")
        print("3. Find restaurants that are open after Y Time and have parking and valet service")
        print("4. Find number of restaurants that are open/closed in a zipcode")
        print("5. Find restaurants in a certain zip code that provides delivery services")
        print("6. Find businesses with review counts greater than X and display hours")
        print("7. Find restaurants in location X where dogs are allowed and wifi is free")
        print("8. Find average star rating for every state. Display the state and the star ratings")
        print("9. Find restaurants in a certain zip code where you don’t have to make reservations")
        print("10. Create users with given parameters")
        print("11. Create business with given parameters")
        print("12. Update user reviews")
        print("13. Update business information")
        print("14. Delete a user based on the user id")
        print("15. Find sum of users who joined yelp since date X")
        print("16. Find top 10 businesses in location X with highest number of check in times")
        print("17. EXIT")
        user_val = input()

        if user_val == '1':
            print("Selected 1")
            print("Use Case: Find top 10 restaurants in location X")
            loc = input("Enter postal code (Ex. 93101): ")
            myVals = []
            print("Processing...")

            results = db.reviewCollection.aggregate([
            { 
                "$match": { "stars": {"$gte":4} } },
                {"$sort": {"stars": -1}},
                { "$limit": 500 },
                {"$project": {"business_id": "$business_id" }}

            ])
            
            for result in results:
                myVals.append(result.get('business_id'))

            endResult = db.businessCollection.find({"postal_code":loc,"business_id":{"$in":myVals}},{"business_id":1,"name":1}).limit(10)
            if len(list(endResult.clone())) > 0:
                for result in endResult:
                    print(result)
            else:
                print("No records found!")

            proceed = input("Press any key to continue ")
            continue
        elif user_val == '2':
            print("Selected 2")
            print("Use Case: List of users who provide the most number of compliments")
            results = db.tipCollection.aggregate([
                {"$group": {"_id":"$compliment_count","user_IDs": {"$push":"$user_id"}}},
                {"$sort":{"_id":-1}},
                {"$limit":1}
                ])
                
            for res in results:
                print(res)

            proceed = input("Press any key to continue ")
            continue


        elif user_val == '3':
            print("Selected 3")
            print("Use Case: Find restaurants that are open after Y Time and have parking and valet service")
            # Get a location hint to narrow down the queries desired
            # loc_hint = input("What zipcode would you like to check? (Or press enter to skip) ")
            # Day input
            day = ''
            day_regex = "Monday|Tuesday|Wednesday|Thursday|Friday|Saturday|Sunday"
            while len(day) <= 0:
                day = input("What day would you like to check? (Monday, Tuesday, Wednesday, Thursday, Friday, Saturday, Sunday)")
                if re.fullmatch(day_regex, day) == None:
                    print("Day not recognized. Please try again.")
                    day = ''
            # Time input
            time_str = ''
            time_regex = "(1?[0-9])|(2[0-4])|([0-9](a|p)m)|(1[0-2](a|p)m)"
            while len(time_str) <= 0:
                time_str = input("After what time should we look for? (Military time 0 - 23 only)")
                if re.fullmatch("1?[0-9]|2[0-3]", time_str) == None:
                    print("Time not recognized. Please try again")
                    time_str = ''
            time_dt = int(time_str)
            # Filter into query
            query = {
                "categories": "Restaurants",
                "attributes.BusinessParking": {"$exists": True},
                "attributes.BusinessParking.valet": True,
                "hours": {"$ne": None}
            }
            res = businessCollection.find(query).limit(30)
            # Since the hours are stored as string, queries need to happen first, then the range
            # can be checked. It might be worthwhile to convert it to a tuple of start and end times.
            valid = []
            for doc in res:
                if day in doc["hours"]:
                    st, ed = doc["hours"][day].split("-")
                    st = int(st.split(":")[0])
                    ed = int(ed.split(":")[0])
                    if time_dt in range(st,ed):
                        valid.append(doc)
            if len(valid) <= 0:
                print("No results found")
            else:
                for doc in valid: print(doc)
            proceed = input("Press any key to continue ")

        elif user_val == '4':
            print("Selected 4")
            print("Use Case: Find number of restaurants that are open/closed in a zipcode")
            loc = input("Enter postal code (Ex. 93101): ")
            res = ""
            op = input("Press 0 for Closed , 1 for Open ")
            if(op == 0):
                res = "Closed"
            else:
                res = "Open"
            results = db.businessCollection.aggregate([
                { "$match": { "$and": [ { "postal_code": { "$eq": loc } }, { "is_open": { "$eq": int(op) } } ] } },
                { "$group": { "_id": "null", "count": { "$sum": 1 } } }
                ])
                
            for result in results:
                print(result.get('count') , "Restaurants are",res,"in postal code",loc)
            proceed = input("Press any key to continue ")

            continue

        elif user_val == '5':
            print("Selected 5")
            print("Use Case: Find restaurants in a certain zip code that provides delivery services.")
            businessZip = input("Enter postal code: ")
            
            restaurants=db.businessCollection.find({"postal_code":businessZip, "attributes.RestaurantsDelivery":"True"},{"business_id":1,"name":1}).limit(10)
            
            if len(list(results.clone())) > 0:
                for res in restaurants:
                    print(res)
            else:
                print("No records found!")
            
            proceed = input("Press any key to continue ")
            
            continue

        elif user_val == '6':
            print("Selected 6") #TODO
        elif user_val == '7':
            print("Selected 7")
            print("Use Case: Find restaurants in location X where dogs are allowed and wifi is free")
            loc = input("Enter postal code (Ex. 93101): ")
            results = db.businessCollection.find({"postal_code":loc,"attributes.WiFi":"u'free'","attributes.DogsAllowed":"True"},{"business_id":1,"name":1}).limit(10)
            if len(list(results.clone())) > 0:
                for result in results:
                    print(result)
            else:
                print("No records found!")
            
            proceed = input("Press any key to continue ")

            continue

        elif user_val == '8':
            print("Selected 8")
            print("Use Case: Find average star rating for every state. Display the state and the star ratings")
            results = db.businessCollection.aggregate([
                {"$group": {_id: "$state", avg_star: {"$avg": "$star"}}},
                { "$limit": 500 },
                {"$project": {state:"$state", avg_star:"$avg_star"}}
            ])

            for result in results:
                print(result)

            proceed = input("Press any key to continue ")

            continue


        elif user_val == '9':
            try:
                print("Selected 9")
                print("Use case: Find restaurants in a certain zip code where you don’t have to make reservations")
                z = input("Enter the postal code to check: ")
                query = {
                    "postal_code": z,
                    "attributes.RestaurantsReservation": False
                }
                res = businessCollection.find(query)
                for r in res:
                    print(result)
            except Exception as e:
                print(e)
            proceed = input("Press any key to continue ")
        elif user_val == '10':
            print("Selected 10")
            print("Use Case: Create user with given parameters")
            name = input("Enter name of the user ")
            reviews = int(input("Enter the number of reviews written by this user "))
            yelp_since = input("Enter the date since the user joined Yelp (format YYYY-MM-DD ")
            post_record = {"name": name,"review_count":reviews,"yelping_since":yelp_since}
            db.userCollection.insert_one(post_record)
            print("Record created")
            results = db.userCollection.find({"name":name,"review_count":reviews,"yelping_since":yelp_since})
            if len(list(results.clone())) > 0:
                for result in results:
                    print(result)
        
            else:
                print("No records found!")

            proceed = input("Press any key to continue ")

            continue

        elif user_val == '11':
            print("Selected 11")
            print("Use Case: Create business with given parameters ")
            businessID = input("Enter the business id: ")
            businessName = input("Enter the name of the business: ")
            businessAddress = input("Enter the address: ")
            business_record = {"business_id": businessID, "name": businessName, "address": businessAddress}
            db.businessCollection.insert_one(business_record)
            print("Business record created")
            results = db.businessCollection.find({"business_id": businessID, "name": businessName, "address": businessAddress})
            if len(list(results.clone())) > 0:
                for result in results:
                    print(result)
            else:
                print("No records found!")
            
            proceed = input("Press any key to continue ")

            continue
           

        elif user_val == '12':
            print("Selected 12")
        elif user_val == '13':
            print("Selected 13")
            print("Use Case: Update business information ")
            businessId = input("Enter the business id ")
            
            print("Displaying Record")

            results = db.businessCollection.find({"business_id":businessId},{"business_id":1,"name":1,"address":1,"city":1})

            if len(list(results.clone())) > 0:
                for result in results:
                    print(result)
        
            else:
                print("No records found!")

            name = input("Enter new name ")
            address = input("Enter new address ")
            city = input("Enter new city ")

            db.businessCollection.update_one({"business_id":businessId},{"$set":{"name":name,"address":address,"city":city}})
            results = db.businessCollection.find({"business_id":businessId},{"business_id":1,"name":1,"address":1,"city":1})
            print("Record Updated")
            if len(list(results.clone())) > 0:
                for result in results:
                    print(result)
        
            else:
                print("No records found!")

            proceed = input("Press any key to continue ")
            continue


        elif user_val == '14':
            print("Selected 14")
            print("Use Case: Delete a user based on the user id ")
            try:
                userID = input("Enter the user id to delete: ")
                db.userCollection.delete_one({"user_id": userID})
                print("Deletion successful")

            except Exception as e:
                print(e)

            proceed = input("Press any key to continue ")
            continue

        elif user_val == '15':
            try:
                print("Selected 15")
                print("Use Case: Find sum of users who joined yelp since date X")
                dt_str = input("Enter a date (YYYY-MM-DD): ")
                y, m, d = dt_str.split("-")
                dt_obj = datetime.datetime(int(y), int(m), int(d))
                pipeline = [
                    {"$match": {"yelping_since": {"$gte": dt_obj}}},
                    {"$count": "yelpers"}
                ]
                res = userCollection.aggregate(pipeline)
                print(res)
            except Exception as e:
                print(e)
            proceed = input("Press any key to continue ")

        elif user_val == '16':
            print("Selected 16")
            print("Use Case: Find top 10 businesses in location X with highest number of check in times")
            loc = input("Enter postal code (Ex. 93101): ")
            agg = [
            {"$match": {"postal_code": { "$eq": loc }}},
            {"$project": {"_id":"$business_id","name":"$name","checkin_count":{ "$size": { "$ifNull": [ "$check-in", [] ] }}}}, 
            {"$sort":{"checkin_count":-1}},
            {"$limit":10}
            ]
            results = db.businessCollection.aggregate(agg,allowDiskUse=True)
            for result in results:
                print(result)

            proceed = input("Press any key to continue ")
            continue

        else:
            print("Terminating")
            break

        break

if __name__ == "__main__":
    main()

