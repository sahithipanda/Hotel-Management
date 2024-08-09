from datetime import datetime
import sqlite3
sc=sqlite3.connect('ABCHotelManagement')
'''query="drop table Rooms"
cursor=sc.cursor()
cursor.execute(query)
sc.commit()
'''
query="create table  IF NOT EXISTS Rooms(RoomID  INTEGER  primary key AUTOINCREMENT,RoomNum int not null,RoomType varchar(10),Price decimal(10,2) not null)"

cursor=sc.cursor()
cursor.execute("PRAGMA foreign_keys=ON;")
cursor.execute(query)

def addRoom():
    RoomNum=int(input("Enter Room Number   :   "))
    RoomType=input("Enter Room Type(Standard,Deluxe,Suite)   :   ")
    Price=input("Enter Price per day   :   ")
   

    query="insert into Rooms(RoomNum,RoomType,Price) values(?,?,?)"
    data=(RoomNum,RoomType,Price)
    cursor=sc.cursor()
    cursor.execute(query,data)
    sc.commit()
    print("\nRoom details added sucessfully!")

def deleteRoom():
    query="select * from Rooms where RoomID=?"
    data=int(input("\nEnter Room ID of the room you want to delete   :   "))
    cursor=sc.cursor()
    cursor.execute(query,(data,))
    row=cursor.fetchone()
    if(row):
        query="delete from Rooms where RoomID=?"
        cursor.execute(query,(data,))
        sc.commit()
        print("\nRoom details deleted Successfully")
    else:
        print("\nRoom  ID not found")
    
    
def viewRooms():
    query="select * from Rooms"
    cursor=sc.cursor()
    cursor.execute(query)
    records=cursor.fetchall()
    if(len(records)!=0):
        print("   RoomID|RoomNum|RoomType|   Price   ")
        print("-"*70)
        for i in records:
            print(f"{" ":5}   {str(i[0]):6}   |   {str(i[1]):7}   |   {str(i[2]):8}   |   {str(i[3]):5}   ")
            #print(tabulate(rows,headers=["RoomID","RoomNum","RoomType","Occupancy","Price","Status"],tablefmt="grid"))
            
while(1):
    ch=int(input("\n\n---------------------Rooms Menu----------------------\n1. Add Room Details\n2. Delete Room Details\n3. View All Rooms\n4. Exit\n\nChoose a valid option   :    "))
    if ch==1:
        addRoom()
    elif ch==2:
        deleteRoom()
    elif ch==3:
        viewRooms()
    elif ch==4:
        break
    else:
        print("Invalid Choice!!")


