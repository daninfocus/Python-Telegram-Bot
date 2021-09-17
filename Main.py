# coding:utf-8
import Constants as keys
from telegram import *
import time
from datetime import datetime, timedelta
import pyodbc


#Te create a .exe file to run the script:
#in the terminal:
#pyinstaller --onefile Main.py

CONNECTION_STRING = 'DRIVER='+'{SQL Server Native Client 11.0}'+';SERVER='+keys.DATABASE_IP + \
    ';DATABASE='+keys.DATABASE_DB+';UID='+keys.DATABASE_USER+';PWD=' + keys.DATABASE_PASSWORD

bot = Bot(keys.API_KEY)

print("Bot started...")
connection = pyodbc.connect(CONNECTION_STRING)

try:
    
    cursor = connection.cursor()    

    today = datetime.today() - timedelta(hours=24)
    today=today.strftime("%Y-%m-%d %H:%M:%S")
    
    print("Connected to SQL Server Native Client")          

    cursor.execute("SELECT t3.*,t1.NewPrice,t1.OldPrice,t1.PriceChanged FROM dbo.PROPERTY_HISTORY t1 INNER JOIN (SELECT MAX(dbo.PROPERTY_HISTORY.Last_Modified) Max_Date, dbo.PROPERTY_HISTORY.Property_Ref FROM dbo.PROPERTY_HISTORY WHERE dbo.PROPERTY_HISTORY.History_Text LIKE '%Public Price been changed%' or dbo.PROPERTY_HISTORY.History_Text LIKE '%To For Sale%' GROUP BY dbo.PROPERTY_HISTORY.Property_Ref) t2 on t1.Property_Ref=t2.Property_Ref JOIN dbo.PROPERTY t3 on t3.Property_Ref=t1.Property_Ref WHERE t1.Last_Modified > (?) and ((t1.History_Text LIKE '%Public Price been changed%' and t1.Last_Modified = t2.Max_Date) or (t1.History_Text LIKE '%To For Sale%' and t1.Last_Modified = t2.Max_Date)) ORDER BY t1.Property_Ref",(today))

    print("Sending messages")   

    region_name = ""
    area_name = ""

    f = open("log.txt", "a")#opens file write
    
    ref="";

    # Loop through the result set
    records = cursor.fetchall()

    for row in records:
        if row[2]!=ref: #this ensures a property doesnt get posted twice

            ref = row[2]
            price = row[11]
            beds = row[17]
            baths = row[18]
            plot = row[19]
            built = row[20]
            newPrice= row[42]
            oldPrice = row[43]
            priceChange = row[44]
            url_contact = "url to website you want to display"


            #database queries for price change, region name and area name.
            #priceChange = cursor.execute("SELECT PriceChanged FROM dbo.PROPERTY_HISTORY WHERE dbo.PROPERTY_HISTORY.Property_Ref=(?) and dbo.PROPERTY_HISTORY.Last_Modified>(?) ORDER BY dbo.PROPERTY_HISTORY.Last_Modified ASC",(ref),(today)).fetchval()

            #oldPrice = cursor.execute("SELECT OldPrice FROM dbo.PROPERTY_HISTORY WHERE dbo.PROPERTY_HISTORY.Property_Ref=(?) and dbo.PROPERTY_HISTORY.Last_Modified>(?)",(ref),(today)).fetchval()
            
            postcode_id = cursor.execute("SELECT Postcode_ID FROM dbo.PROPERTY where Property_Ref=(?)", (ref)).fetchval()

            region_name = cursor.execute("SELECT Region_Name FROM dbo.PC_REGION join dbo.POSTCODE on dbo.PC_REGION.Region_ID=dbo.POSTCODE.Region_ID where dbo.POSTCODE.Postcode_ID=(?)", (postcode_id)).fetchval()
            
            area_name = cursor.execute("SELECT Area_Name FROM dbo.PC_AREA join dbo.POSTCODE on dbo.PC_AREA.Area_ID=dbo.POSTCODE.Area_ID where dbo.POSTCODE.Postcode_ID=(?)", (postcode_id)).fetchval()

            

            #telegram message concatenation
            my_message = "🛏 " + str(beds) + " beds\n"
            my_message += "🛁 " + str(baths) + " baths\n"
            my_message += "🏡 " + str(built) + "m² built / " + str(plot) + "m² plot\n"
            
            if priceChange == 1:
                my_message += "💵 €" +str(newPrice)+" (was €"+str(oldPrice)+")"  + "\n"
            else:
                my_message += "💵 €" + str(price)  + "\n"

            my_message += "📄 Ref: " + ref + "\n"
            my_message += "📍 " + area_name + ", " + region_name + "\n"
            my_message += "👉🏻 " + url_contact + "\n"


            print (ref)

            #apending the photos to the message, the message will be on the first image, to correctly display the data
            photos = []
            photos.append(InputMediaPhoto("url to photo", my_message))
            photos.append(InputMediaPhoto("url to photo"))
            photos.append(InputMediaPhoto("url to photo"))


            #depending on price it uses a different chat id for the different telegram channels
            if price < 50000:
                chat_id=keys.CHAT_ID_LESS_THAN_50k

                #log
                log = ref+";"+str(price)+";"+str(datetime.today().strftime("%Y-%m-%d %H:%M:%S"))+";"+"<50k"+"\n"
                f.write(log)

                bot.sendChatAction(chat_id, 'typing')
                time.sleep(1)
                bot.sendMediaGroup(chat_id, photos)
                time.sleep(5)
            if price >=50000 and price <=100000:
                chat_id=keys.CHAT_ID_BETWEEN_50k_100k

                #log
                log = ref+";"+str(price)+";"+str(datetime.today().strftime("%Y-%m-%d %H:%M:%S"))+";"+"50-100k"+"\n"
                f.write(log)

                bot.sendChatAction(chat_id, 'typing')
                time.sleep(1)
                bot.sendMediaGroup(chat_id, photos)
                time.sleep(5)
            if price >=100000 and price <=150000:
                chat_id=keys.CHAT_ID_BETWEEN_100k_150k

                #log
                log = ref+";"+str(price)+";"+str(datetime.today().strftime("%Y-%m-%d %H:%M:%S"))+";"+"100-150k"+"\n"
                f.write(log)

                bot.sendChatAction(chat_id, 'typing')
                time.sleep(1)
                bot.sendMediaGroup(chat_id, photos)
                time.sleep(5)
            if price >=150000 and price <=250000:
                chat_id=keys.CHAT_ID_BETWEEN_150k_250k

                #log
                log = ref+";"+str(price)+";"+str(datetime.today().strftime("%Y-%m-%d %H:%M:%S"))+";"+"150-250k"+"\n"
                f.write(log)

                bot.sendChatAction(chat_id, 'typing')
                time.sleep(1)
                bot.sendMediaGroup(chat_id, photos)
                time.sleep(5)
            if price >250000:
                chat_id=keys.CHAT_ID_MORE_THAN_250k


                #log
                log = ref+";"+str(price)+";"+str(datetime.today().strftime("%Y-%m-%d %H:%M:%S"))+";"+">250k"+"\n"
                f.write(log)

                bot.sendChatAction(chat_id, 'typing')
                time.sleep(1)
                bot.sendMediaGroup(chat_id, photos)
                time.sleep(5)


    f.close() #close file write
except pyodbc.Error as error:
    print("Failed to read data from table", error)
if (connection):
    connection.close()
    print("The SQL Server Native connection is closed")




