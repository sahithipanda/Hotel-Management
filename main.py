from flask import Flask,render_template,request,send_from_directory,request,url_for,redirect,session
from datetime import datetime
import sqlite3
import random
import warnings

warnings.filterwarnings("ignore",category=DeprecationWarning)

conn = sqlite3.connect('ABCHotelManagement')

cursor = conn.cursor()
cursor.execute("create table IF NOT EXISTS Customer (User_ID int primary  key,Name varchar(50), Email varchar(50), Code int, Mobile_Number int, Address varchar(100), Password varchar(30))")
conn.commit()
query="create table  IF NOT EXISTS Reservation(Reservation_ID  int primary key,User_ID int,Booking_Date date, Check_In date,Check_Out date,Room_Type varchar(10),Room_Number int,Bill_Amount decimal(10,2) default NULL,Status varchar(15),Payment_Status varchar(15), foreign key(User_ID) references Customer(User_ID) )"
cursor.execute("PRAGMA foreign_keys=ON;")
cursor.execute(query)
conn.commit()
query="create table  IF NOT EXISTS Rooms(RoomID  INTEGER  primary key AUTOINCREMENT,RoomNum int not null,RoomType varchar(10),Price decimal(10,2) not null)"
cursor.execute(query)
conn.commit()
query="create table  IF NOT EXISTS Bill(Bill_ID INTEGER  primary key AUTOINCREMENT, Reservation_ID varchar(10),Num_Room_Services int default 0,Num_Laundry int default 0,Food int default 0,Total decimal(10,2),Payment_ID varchar(10), foreign key(Reservation_ID) references Reservation(Reservation_ID))"
cursor.execute(query)
conn.commit()

app=Flask(__name__)
app.secret_key='123456789'


@app.route('/',endpoint="main")
def main():
    return render_template('loginpage.html')


@app.route('/login',methods=['GET','POST'])
def login():
    if request.method=='POST':
        username=request.form["username"]
        password=request.form["pwd"]
        session['User_ID']=username
        with sqlite3.connect('ABCHotelManagement') as conn:
            cursor = conn.cursor()
            query = "select name from Admin where user_Id=? and Password=?"
            data=(username,password)
            cursor.execute(query,data)
            records=cursor.fetchone()
            if records:
                name=records[0]
                session['Name']=name
                return redirect(url_for('adminHomePage'))
            else:
                query="select name from Customer where User_ID=? and Password=?"
                data=(username,password)
                cursor.execute(query,data)
                records=cursor.fetchone()
                if(records):
                    name=records[0]
                    session['Name']=name
                    return redirect(url_for('home'))
                else:
                    return render_template('loginpage.html', username=username,error=True)
    else:
        return render_template('loginpage.html',error=False)


@app.route('/register',methods=['GET','POST'])
def register():
    if request.method=='POST':
        Name=request.form["name"]
        Email=request.form["email"]
        Code=request.form["code"]
        Mobile_Number=request.form["num"]
        Address=request.form["address"]
        Password=request.form["pwd"]

        while True:
            unique_id=''.join(random.choices('123456789',k=1))+''.join(random.choices('0123456789',k=4))
            with sqlite3.connect('ABCHotelManagement') as conn:
                query="select * from Customer where User_ID=?"
                cursor=conn.cursor()
                cursor.execute(query,(unique_id,))
                records=cursor.fetchall()
                if len(records)==0:
                    break
        try:
            with sqlite3.connect('ABCHotelManagement') as conn:
                data=(unique_id,Name,Email,Code,Mobile_Number,Address,Password)
                cursor=conn.cursor()
                cursor.execute("insert into Customer ( User_ID,Name, Email,Code,Mobile_Number, Address,Password) values (?,?,?,?,?,?,?)",data)
                conn.commit()
                return render_template('success.html',username=Name,userId=unique_id)
        except sqlite3.Error as e:
            print(e)
    else:
        return render_template('register.html')


@app.route('/home')
def home():
    return render_template('homepage.html',Name=session.get('Name'))


@app.route('/reservation',methods=['GET','POST'])
def reservation():

    #generating reservationID
    def gen():
        while True:
            cursor=conn.cursor()
            unique_id=''.join(random.choices('ABCDEFGHIJKLMNOPQRSTUVWXYZ',k=2))+''.join(random.choices('0123456789',k=3))
            query="select * from Reservation where Reservation_ID=?"
            cursor.execute(query,(unique_id,))
            records=cursor.fetchall()
            if len(records)==0:
                return unique_id
            
    if request.method=='POST':
        Check_In=request.form["checkindate"]
        Check_Out=request.form["checkoutdate"]
        Room_Type=request.form["roompref"]
        User_ID=session.get('User_ID')
        Booking_Date=datetime.today().date()
        Payment_Status="pending"
        Status="pending"
        with sqlite3.connect('ABCHotelManagement') as conn:
            cursor=conn.cursor()
            query="select RoomNum from Rooms where RoomType=? and RoomNum not in (select Room_Number from reservation where ( (? BETWEEN Check_In and Check_Out) or (? BETWEEN Check_In and Check_Out ) ))"
            cursor.execute(query,(Room_Type,Check_In,Check_Out))
            records=cursor.fetchone()
            if(records):
                Room_Number=str(records[0])
                unique_id=gen()
                query="insert into Reservation (Reservation_ID,User_ID,Booking_Date,Check_In,Check_Out,Room_Type,Room_Number,Status,Payment_Status) values(?,?,?,?,?,?,?,?,?)"
                data=(unique_id,User_ID,Booking_Date,Check_In,Check_Out,Room_Type,Room_Number,Status,Payment_Status)
                cursor.execute(query,data)
                conn.commit()
                query="insert into Bill (Reservation_ID) values(?)"
                cursor.execute(query,(unique_id,))
                conn.commit()
                return render_template('reservationconfirmation.html',Reservation_ID=unique_id,Room_Number=Room_Number)
            else:
                return render_template('reservation.html',Name=session.get('Name'),error=True)
            
 
    else:
        return render_template('reservation.html',Name=session.get('Name'))


@app.route('/billing',methods=['GET','POST'])
def userbilling():
    if request.method=='POST':
        Reservation_ID=request.form['Reservation_ID']
        with sqlite3.connect('ABCHotelManagement') as conn:
            cursor=conn.cursor()
            query="select Check_In,Check_Out,Room_Type from Reservation where Reservation_ID=?"
            cursor.execute(query,(Reservation_ID,))
            r=cursor.fetchone()
            cin=r[0]
            cout=r[1]
            pref=r[2].lower()
            cursor.execute("select julianday(?)-julianday(?)",(cout,cin,))
            diff=int(cursor.fetchone()[0])
            cursor.execute("select Service_Price from Services where Service_Name=?",(pref,))
            prefprice=cursor.fetchone()
            prefprice=prefprice[0]
            cursor.execute("select Service_Price from Services where Service_Name=?",("rmservices",))
            rmsp=cursor.fetchone()
            rmsp=rmsp[0]
            cursor.execute("select Service_Price from Services where Service_Name=?",("laundry",))
            lp=cursor.fetchone()
            lp=lp[0]
            cursor.execute("select Service_Price from Services where Service_Name=?",("food",))
            fp=cursor.fetchone()
            fp=fp[0]
            cursor.execute("select Service_Price from Services where Service_Name=?",("tax",))
            tp=cursor.fetchone()
            tp=tp[0]

            cursor.execute("select Num_Room_Services,Num_Laundry,Food from Bill where Reservation_ID=?",(Reservation_ID,))
            re=cursor.fetchone()
            nr=re[0]
            nl=re[1]
            nf=re[2]

            subtotal=prefprice*diff
            addser=(nr*rmsp)+(nl*lp)+(nf*fp)

            add=((subtotal+addser)*tp)/100
            ttx = add*2
            totalbill=subtotal+addser+(add*2)
            cursor.execute("update Bill set Total=? where Reservation_ID=?",(totalbill,Reservation_ID,))
            cursor.execute("update Reservation set Bill_Amount=? where Reservation_ID=?",(totalbill,Reservation_ID,))
            conn.commit()
        return render_template('userbilling.html',Name=session.get('Name'),Reservation_ID=Reservation_ID,prefprice=prefprice,pref=pref,diff=diff,subtotal=subtotal,roomserv=rmsp*nr,laundry=nl*lp,food=nf*fp,addser=addser,tax=tp,add=add,ttx=ttx,totalbill=totalbill)
    else:
        with sqlite3.connect('ABCHotelManagement') as conn:
            cursor=conn.cursor()
            User_ID=session.get('User_ID')
            data=(User_ID,"waiting")
            query="select Reservation_ID,Booking_Date,Check_In,Check_Out,Room_Type from Reservation where User_ID=? and Payment_Status=?"
            cursor.execute(query,data)
            reservations=cursor.fetchall()
            if len(reservations) == 0:
                return render_template('pendingpayments.html',Name=session.get('Name'), err=True)
        return render_template('pendingpayments.html',Name=session.get('Name'),reservations=reservations,err=False)


@app.route('/billing/userinvoice/')
def userinvoice(Reservation_ID):
    return render_template('userbilling.html',Name=session.get('Name'))


@app.route('/bookinghistory')
def userbookinghistory():
    with sqlite3.connect('ABCHotelManagement') as conn:
        cursor=conn.cursor()
        User_ID=session.get('User_ID')
        today=datetime.today().date()
        data=(User_ID,today)
        query="select Reservation_ID,Booking_Date,Check_In,Check_Out,Room_Type,Room_Number,Bill_Amount from Reservation where User_ID=? and Check_In<?"
        cursor.execute(query,data)
        history=cursor.fetchall()
    if len(history) == 0:
        return render_template('userbookinghistory.html',Name=session.get('Name'),history=history, err=True)
    else:
        return render_template('userbookinghistory.html',Name=session.get('Name'),history=history, err=False)


@app.route('/upcomingbookings')
def upcomingbookings():
    with sqlite3.connect('ABCHotelManagement') as conn:
        cursor=conn.cursor()
        User_ID=session.get('User_ID')
        today=datetime.today().date()
        data=(User_ID,today, "rejected")
        query="select Reservation_ID,Booking_Date,Check_In,Check_Out,Room_Type,Room_Number,Status,Payment_Status from Reservation where User_ID=? and Check_In>=? and Status!=?"
        cursor.execute(query,data)
        upcoming=cursor.fetchall()
    if len(upcoming) == 0:
        return render_template('userbookings.html',Name=session.get('Name'),upcoming=upcoming, err=True)
    else:
        return render_template('userbookings.html',Name=session.get('Name'),upcoming=upcoming, err=False)


@app.route('/contactsupport')
def contactsupport():
    return render_template('contactsupport.html',Name=session.get('Name'))


@app.route('/updateFeedback', methods=['POST'])
def updateFeedBack():
    if request.method=='POST':
        
        #update query
        
        return render_template("homepage.html")
    return render_template("homepage.html")

@app.route("/paymentModeSelect", methods=['POST'])
def modeSelect():
    if request.method == 'POST':
        totalbill=request.form['totalbill']
        Reservation_ID = request.form['Reservation_ID']
        return render_template("payment.html",Name=session.get('Name'), totalbill=totalbill, Reservation_ID=Reservation_ID)


@app.route('/paymentmode',methods=['GET','POST'])
def paymentmode():
    if request.method=='POST':
        Reservation_ID = request.form['Reservation_ID']
        totalbill = request.form['totalbill']
        mode=request.form['mode']
        if mode=='credit':
            return render_template('/paynowcredit.html',Name=session.get('Name'), totalbill=totalbill, Reservation_ID=Reservation_ID)
        elif mode=='debit':
            return render_template('/paynowdebit.html', Name=session.get('Name'),totalbill=totalbill, Reservation_ID=Reservation_ID)
    else:
        price=request.form['totalbill']
        return render_template('payment.html',Name=session.get('Name'),Reservation_ID=Reservation_ID)

@app.route('/credit', methods=['POST'])
def creditmode():
    #update billing
    if request.method=='POST':
        Reservation_ID=request.form['Reservation_ID']
        with sqlite3.connect('ABCHotelManagement') as conn:
            cursor=conn.cursor()
            cursor.execute("update Reservation SET Payment_Status=? WHERE Reservation_ID=?",("paid",Reservation_ID,) )
            conn.commit()
    return render_template("paymentSuccess.html",Name=session.get('Name'), succmsg=True)

@app.route('/debit', methods=['POST'])
def debitmode():
    #updatebilling
    if request.method=='POST':
        Reservation_ID=request.form['Reservation_ID']
        with sqlite3.connect('ABCHotelManagement') as conn:
            cursor=conn.cursor()
            cursor.execute("update Reservation SET Payment_Status=? WHERE Reservation_ID=?",("paid",Reservation_ID,) )
            conn.commit()
    return render_template("paymentSuccess.html", Name=session.get('Name'), succmsg=True)


@app.route('/complaint')
def complaint():
    return render_template("complaint.html", Name=session.get('Name'))


@app.route('/updateComplaint', methods=['POST'])
def updateComplaint():
    if request.method=="POST":

        #

        return render_template("homepage.html", Name=session.get('Name'))
    return render_template("homepage.html", Name=session.get('Name'))

@app.route('/logout')
def logout():
    session.clear()
    return render_template('logout.html')

@app.route("/adminHome")
def adminHomePage():
    return render_template('adminhomepage.html', Name=session.get('Name'))


@app.route("/adminReservation")
def adminReservationPage():
    with sqlite3.connect('ABCHotelManagement') as conn:
        cursor=conn.cursor()
        query="select User_ID, Reservation_ID, Room_Type, Check_In, Check_Out from Reservation where Status=?"
        data=("pending",)
        cursor.execute(query,data)
        reservations=cursor.fetchall()
        if len(reservations) == 0:
            return render_template("pendingreservations.html", Name=session.get('Name'), nothing=True)
        else:
            return render_template("pendingreservations.html", Name=session.get('Name'), nothing=False, reservations=reservations)


@app.route("/adminReservationAction", methods=['POST'])
def adminReservationActionPage():
    if request.method=='POST':
        Reservation_ID=request.form['Reservation_ID']
        with sqlite3.connect('ABCHotelManagement') as conn:
            cursor=conn.cursor()
            query="select User_ID, Room_Type, Check_In, Check_Out from Reservation where Reservation_ID=?"
            data=(Reservation_ID,)
            cursor.execute(query,data)
            details=cursor.fetchone()
        return render_template('adminreservation.html', Reservation_ID=Reservation_ID, details=details, Name=session.get('Name'))


@app.route("/updateReservation", methods=['POST'])
def updateReservation():
    if request.method == 'POST':
        Reservation_ID = request.form['Reservation_ID']
        approvalstatus = request.form['approvalstatus']
        if approvalstatus == "approved":
            #update status as approved
            with sqlite3.connect('ABCHotelManagement') as conn:
                cursor=conn.cursor()
                query = "UPDATE Reservation SET Status = ? WHERE Reservation_ID =?"
                data = (approvalstatus, Reservation_ID)
                cursor.execute(query,data)
        else:
            #update status as rejected
            rejDesc = request.form['rejectionDescription']
            with sqlite3.connect('ABCHotelManagement') as conn:
                cursor=conn.cursor()
                rejectionDescription = request.form['rejectionDescription']
                query = "UPDATE Reservation SET Status=?, RejectDescription=? WHERE Reservation_ID=?"
                data = (approvalstatus, rejDesc, Reservation_ID)
                cursor.execute(query,data)
        return redirect(url_for('adminReservationPage'))


@app.route("/adminBilling")
def adminBillingPage():
    return render_template('adminbilling.html', Name=session.get('Name'), err="one")

@app.route("/adminBillinginvoice", methods=['POST'])
def adminBilling():
    if request.method=='POST':
        Reservation_ID = request.form['Reservation_ID']
        with sqlite3.connect('ABCHotelManagement') as conn:
            cursor=conn.cursor()
            query = "select User_ID, Room_Type, Room_Number, julianday(Check_Out) - julianday(Check_In) FROM Reservation where Reservation_ID=?"
            data = (Reservation_ID,)
            res = cursor.execute(query,data)
            res1 = res.fetchone()
            if res1 == None:
                return render_template('adminbilling.html', Name=session.get('Name'), err="two")
            
            User_ID = res1[0]
            Room_Type = res1[1]
            Room_Number = res1[2]
            num_days = int(res1[3])

            query = "select Name, Mobile_Number from customer where User_ID=?"
            data = (User_ID,)
            res = cursor.execute(query,data)
            res2 = res.fetchone()

            name = res2[0]
            Mobile_Number = res2[1]

            query = "select Num_Room_Services, Num_Laundry, Food from Bill where Reservation_ID=?"
            data=(Reservation_ID,)
            res = cursor.execute(query,data)
            res3 = res.fetchone()

            Num_Room_Services = int(res3[0])
            Num_Laundry = int(res3[1])
            Num_Food = int(res3[2])

            query="select Service_Price from Services"
            res = cursor.execute(query)
            res4 = res.fetchall()

            if Room_Type == "Standard":
                rmch = int(res4[0][0])
            elif Room_Type == "Deluxe":
                rmch = int(res4[1][0])
            elif Room_Type == "Suite":
                rmch = int(res4[2][0])
            else:
                rmch=0
            rmserv = int(res4[3][0])
            Laundry = int(res4[4][0])
            Food = int(res4[5][0])
            tax = int(res4[6][0])

            subtotal = rmch*num_days

            totRmserv = Num_Room_Services*rmserv
            totLaund = Num_Laundry*Laundry
            totFood = Num_Food*Food
            tot_addit = totRmserv+totLaund+totFood

            suby = subtotal+tot_addit
            tx_val = (suby*tax)/100
            ttxx = tx_val*2
            totalbill = suby + ttxx
            values = (Reservation_ID, User_ID, name, Mobile_Number, Room_Type, Room_Number, rmch, num_days, subtotal, Num_Room_Services, totRmserv, Num_Laundry, totLaund, Num_Food, totFood, tot_addit, tax, tx_val, ttxx,totalbill)

        return render_template("adminbilling.html", Name=session.get('Name'), Reservation_ID=Reservation_ID, User_ID=User_ID, name=name, Mobile_Number=Mobile_Number, Room_Type=Room_Type, Room_Number=Room_Number, rmch=rmch, num_days=num_days, subtotal=subtotal, Num_Room_Services=Num_Room_Services, totRmserv=totRmserv, Num_Laundry=Num_Laundry, totLaund=totLaund, Num_Food=Num_Food, totFood=totFood, tot_addit=tot_addit, tax=tax, tx_val=tx_val, ttxx=ttxx, totalbill=totalbill, err="three")
    else:
        return render_template("adminbilling.html", Name=session.get('Name'), err="one")


@app.route("/updateBilling", methods=['POST'])
def updateAdminBilling():
    if request.method=='POST':
        Reservation_ID=request.form['Reservation_ID']
        totalbill = request.form['totalbill']
        with sqlite3.connect('ABCHotelManagement') as conn:
            cursor=conn.cursor()
            query = "UPDATE Reservation SET Bill_Amount=?, Payment_Status=? WHERE Reservation_ID=?"
            data=(totalbill, "waiting", Reservation_ID,)
            cursor.execute(query,data)
            conn.commit()
        return redirect(url_for('adminBillingPage'))
    else:
        return render_template("adminbilling.html", Name=session.get('Name'), err="one")

@app.route("/adminServices")
def adminServiesPage():
    return render_template('adminServices.html', Name=session.get('Name'))


@app.route("/adminServicesValidate", methods=['POST'])
def updateServicesValidate():
    if request.method == 'POST':
        resID = request.form['resID'].upper()
        with sqlite3.connect('ABCHotelManagement') as conn:
            cursor=conn.cursor()
            query="select Reservation_ID,Num_Room_Services,Num_Laundry,Food from Bill where Reservation_ID=?"
            cursor.execute(query,(resID,))
            records=cursor.fetchone()
            if records:
                rsused=int(records[1])
                lused=int(records[2])
                fused=int(records[3])
                return render_template('adminServices.html', resID=resID, rsused=rsused, lused=lused, fused=fused, valid=True)
            else:
                return render_template('adminServices.html', resID=resID, invalid=True)


@app.route("/adminServicesUpdate", methods=['POST'])
def updateServicesUsed():
    if request.method == 'POST':
        resID = request.form['resID']
        rsused=request.form['rmsu']
        lused=request.form['laundry']
        fused=request.form['food']
        
        with sqlite3.connect('ABCHotelManagement') as conn:
            cursor=conn.cursor()
            query="update Bill set Num_Room_Services=?,Num_Laundry=?,Food=?  where Reservation_ID=?"
            cursor.execute(query,(rsused,lused,fused,resID,))
            conn.commit()
        return render_template('adminServices.html', aler=True)


@app.route("/adminHistory")
def adminHistory():
    return render_template('adminhistory.html', Name=session.get('Name'), err="one")


@app.route('/adminHistoryData',methods=['GET','POST'])
def adminhistoryData():
    if request.method=='POST':
        User_ID=request.form['User_ID']
        with sqlite3.connect('ABCHotelManagement') as conn:
            cursor=conn.cursor()
            query="select Reservation_ID,Booking_Date,Check_In,Check_Out,Room_Type,Room_Number,Status,Payment_Status,Bill_Amount from Reservation where User_ID=? and Check_In<=?"
            today=datetime.today().date()
            cursor.execute(query,(User_ID,today))
            history=cursor.fetchall()
            if len(history) == 0:
                return render_template('adminhistory.html', Name=session.get('Name'), User_ID=User_ID, err="two")
            else:
                return render_template('adminhistory.html',Name=session.get('Name'),User_ID=User_ID, history=history, err="three")
    else:
        return redirect(url_for('adminHistory'))


@app.route("/adminBookings")
def adminBookingsPage():
    return render_template('adminbookings.html', Name=session.get('Name'),err="one")


@app.route("/adminBookingsData",methods=['GET','POST'])
def adminBookingsData():
    if request.method=='POST':
        User_ID=request.form['User_ID']
        with sqlite3.connect('ABCHotelManagement') as conn:
            cursor=conn.cursor()
            query="select Reservation_ID,Booking_Date,Check_In,Check_Out,Room_Type,Room_Number,Status,Payment_Status,Bill_Amount from Reservation where User_ID=? and Check_Out<?"
            today=datetime.today().date()
            cursor.execute(query,(User_ID,today))
            history=cursor.fetchall()
            if len(history) == 0:
                return render_template('adminbookings.html', Name=session.get('Name'), User_ID=User_ID, err="two")
            else:
                return render_template('adminbookings.html',Name=session.get('Name'),User_ID=User_ID, history=history, err="three")
    else:
        return redirect(url_for('adminBookingsPage'))


@app.route("/adminRoomStatus")
def adminRoomStatusPage():
    return render_template('adminroomstatus.html', Name=session.get('Name'))


@app.route("/adminContactSupport")
def adminContactSupportPage():
    return render_template('adminContactSupport.html', Name=session.get('Name'))


@app.route("/adminCosts")
def adminCostsPage():

    with sqlite3.connect('ABCHotelManagement') as conn:
        cursor=conn.cursor()
        Name=session.get('Name')
        query="select Service_Price from Services"
        cursor.execute(query)
        costs=cursor.fetchall()

    return render_template('admincosts.html',Name=Name,standard=costs[0][0],deluxe=costs[1][0],suite=costs[2][0],rmserv=costs[3][0],laundry=costs[4][0],food=costs[5][0],tax=costs[6][0])

@app.route("/updateCosts", methods=['POST'])
def updateCosts():
    if request.method == 'POST':
        standard = request.form['standard']
        deluxe = request.form['deluxe']
        suite = request.form['suite']
        rmserv = request.form['rmserv']
        laundry = request.form['laundry']
        food = request.form['food']
        tax = request.form['tax']
        with sqlite3.connect('ABCHotelManagement') as conn:
            cursor=conn.cursor()
            cursor.execute("update Services set Service_Price=? where Service_Name=?",(standard,"Standard",))
            cursor.execute("update Services set Service_Price=? where Service_Name=?",(deluxe,"Deluxe",))
            cursor.execute("update Services set Service_Price=? where Service_Name=?",(suite,"Suite",))
            cursor.execute("update Services set Service_Price=? where Service_Name=?",(rmserv,"rmservices",))
            cursor.execute("update Services set Service_Price=? where Service_Name=?",(laundry,"laundry",))
            cursor.execute("update Services set Service_Price=? where Service_Name=?",(food,"food",))
            cursor.execute("update Services set Service_Price=? where Service_Name=?",(tax,"tax",))

        return render_template("adminhomepage.html", costUpd=True)



if __name__=="__main__":
    app.run(debug=True)
    
    
