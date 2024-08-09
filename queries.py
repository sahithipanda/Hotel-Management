import sqlite3
from datetime import datetime
sc=sqlite3.connect('ABCHotelManagement')

cursor=sc.cursor()
'''
cursor.execute("PRAGMA foreign_keys=ON;")
cursor.execute(query)
'''


'''
cursor.execute("insert into Services  values(?,?)",('Standard',1800,))
cursor.execute("insert into Services  values(?,?)",('Deluxe',2800,))
cursor.execute("insert into Services  values(?,?)",('Suite',3800,))
cursor.execute("insert into Services  values(?,?)",('rmservices',199,))
cursor.execute("insert into Services  values(?,?)",('laundry',249,))
cursor.execute("insert into Services  values(?,?)",('food',399,))
cursor.execute("insert into Services  values(?,?)",('tax',7,))

sc.commit()
'''
'''
cursor.execute("delete from Services")
query="create table  IF NOT EXISTS Services(Service_Name varchar(30)  primary key,Service_Price decimal(10,2) not null)"
cursor.execute("insert into Services  values(?,?)",('Standard',1800,))
cursor.execute("insert into Services  values(?,?)",('Deluxe',2800,))
cursor.execute("insert into Services  values(?,?)",('Suite',3800,))
cursor.execute("insert into Services  values(?,?)",('rmservices',199,))
cursor.execute("insert into Services  values(?,?)",('laundry',249,))
cursor.execute("insert into Services  values(?,?)",('food',399,))
cursor.execute("insert into Services  values(?,?)",('tax',7,))

'''
'''#cursor.execute("drop table Admin")
cursor.execute("create table IF NOT EXISTS Admin (User_ID int primary  key,Name varchar(20),Password varchar(30))")
cursor.execute("insert into Admin  values(?,?,?)",(98765,'Robin','Admin@123',))
cursor.execute("insert into Admin  values(?,?,?)",(98764,'Aisha','Admin@234',))
cursor.execute("insert into Admin  values(?,?,?)",(98763,'David','Admin@345',))


'''
'''query="insert into Reservation (Reservation_ID,User_ID,Booking_Date,Check_In,Check_Out,Room_Type,Room_Number,Status,Payment_Status) values(?,?,?,?,?,?,?,?,?)"
data=("FCH88",22544,"2024-04-22","2024-04-24","2024-04-26","standard",101,"approved","pending")
cursor.execute(query,data)
sc.commit()
query="insert into Bill (Reservation_ID) values(?)"
cursor.execute(query,("FCH88",))
sc.commit()
query="select *  from Reservation"

#cursor.execute("delete from  Reservation")
#query="create table  IF NOT EXISTS Bill(Bill_ID INTEGER  primary key AUTOINCREMENT, Reservation_ID varchar(10),Num_Room_Services int default 0,Num_Laundry int default 0,Food int default 0,Total decimal(10,2),Payment_ID varchar(10), foreign key(Reservation_ID) references Reservation(Reservation_ID))"
#cursor.execute(query)

#cursor.execute("delete from Services")
cursor.execute("insert into Services  values(?,?)",('standard',1800,))
cursor.execute("insert into Services  values(?,?)",('deluxe',2800,))
cursor.execute("insert into Services  values(?,?)",('suite',3800,))
cursor.execute("insert into Services  values(?,?)",('rmservices',199,))
cursor.execute("insert into Services  values(?,?)",('laundry',249,))
cursor.execute("insert into Services  values(?,?)",('food',399,))
cursor.execute("insert into Services  values(?,?)",('tax',7,))
query="select *  from Services"'''
#query="insert into Reservation (Reservation_ID,User_ID,Booking_Date,Check_In,Check_Out,Room_Type,Room_Number,Status,Payment_Status)"
#Reservation_ID = "SM544"
#query="select User_ID, Room_Type, Check_In, Check_Out, Status, Room_Number from Reservation where Reservation_ID=?"
#data=(Reservation_ID,)
#query = "ALTER TABLE Reservation ADD RejectDescription VARCHAR(50)"
#query = "UPDATE Reservation SET Status=?, RejectDescription=? WHERE Reservation_ID=?"
#data=("rejected", "No Reason", "SM544")
#cursor.execute(query,data)

#cursor.execute(query)
#r=cursor.fetchall()
#print(r)
#sc.commit()

'''
query = "UPDATE Reservation SET Status = ? WHERE Reservation_ID =?"
data = ("approved", Reservation_ID)
cursor.execute(query,data)
'''
'''
query="select User_ID, Room_Type, Check_In, Check_Out, julianday(Check_Out) - julianday(Check_In), Status, RejectDescription from Reservation where Reservation_ID=?"
data=("SM544",)
cursor.execute(query,data)
#cursor.execute(query)
r=cursor.fetchall()
print(r)'''
'''
Reservation_ID="SM544"
query = "select User_ID, Room_Type, Room_Number, julianday(Check_Out) - julianday(Check_In) FROM Reservation where Reservation_ID=?"
data = (Reservation_ID,)
res = cursor.execute(query,data)
res1 = res.fetchone()
User_ID = res1[0]
print(res1)

query = "select Name, Mobile_Number from customer where User_ID=?"
data = (User_ID,)
res = cursor.execute(query,data)
res2 = res.fetchone()
print(res2)

query = "select Num_Room_Services, Num_Laundry, Food from Bill where Reservation_ID=?"
data=(Reservation_ID,)
res = cursor.execute(query,data)
res3 = res.fetchone()
print(res3)

rmtype=res1[1]
query="select Service_Price from Services"
res = cursor.execute(query)
res4 = res.fetchall()

print(res4)
if rmtype == "Standard":
    rmch = res4[0][0]
elif rmtype == "Deluxe":
    rmch = res4[1][0]
elif rmtype == "Suite":
    rmch = res4[2][0]
else:
    print("None")

print("\nuserID : ", res1[0])
print("Name : ", res2[0])
print("Mobile : ", res2[1])
print("Room Type : ", res1[1])
print("Room Numb : ", res1[2])

print("per day room : ", rmch)
print("number of days : ", res1[3])
print("Sub total : ", rmch*res1[3])


print("\nRoom Service ("+str(res3[0])+" times) : "+str(int(res3[0])*int(res4[3][0])))
print("Laundry Service ("+str(res3[1])+" times) : "+str(int(res3[1])*int(res4[4][0])))
print("Food  ("+str(res3[2])+" times) : "+str(int(res3[2])*int(res4[5][0])))
print("Additinal charges : \n")

print("taxes( "+str(res4[6][0])+"%) : "+str(int(rmch)*int(res1[3])*int(res4[6][0])))'''
'''
today=datetime.today().date()

data=("29082",today,)
query="select User_ID, Reservation_ID,Booking_Date,Check_In,Check_Out,Room_Type,Room_Number,Status,Payment_Status from Reservation where User_ID=? and Check_In>=?"
res = cursor.execute(query,data)'''

res = cursor.execute("select Payment_ID from Bill where Reservation_ID=?", ("SM544",))
res4 = res.fetchall()
print(res4)