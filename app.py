from flask import Flask, jsonify, redirect, url_for, request
from flask_cors import CORS
from flask_jwt_extended import  create_access_token, get_jwt, get_jwt_identity \
                                ,unset_jwt_cookies, jwt_required, JWTManager
from datetime import datetime, timedelta, timezone, date
import json
from werkzeug.security import generate_password_hash, check_password_hash
from werkzeug.utils import secure_filename
import os
import base64
from flask_mysqldb import MySQL


app = Flask(__name__)
CORS(app)

app.config["JWT_SECRET_KEY"] = "0d51f3ad3f5aw0da56sa"
app.config["JWT_ACCESS_TOKEN_EXPIRES"] = timedelta(hours=1)
jwt = JWTManager(app)

image_folder = os.path.abspath("static/images")

mock_users_data = {"s6401012620234":{"name":"Supakorn","lastname":"Pholsiri","major":"Cpr.E","year":2,"password":generate_password_hash("123456")}}
mock_admins_data = {"08spn491324619":{"name":"Supa","lastname":"Phol","depart":"Cpr.E","password":generate_password_hash("4567")}}


mock_equipment_data = [("456135461451","GRCD-4658131-4616","Generator","Electrical source","Unavailable","Robotic lab","456135461451.jpg"), ("545196164665","SUNWA-1962","Multimeter","Measurement","Available","Electrical lab","545196164665.jpeg")]
mock_material_data = []

mock_borrow_data = [("456135461451","s6401012620234", date(2023,3,19).strftime('%Y-%m-%d'), date(2023,4,19).strftime('%Y-%m-%d'), "08spn491324619")]

mysql = MySQL(app)

@app.route('/admin_equipment',methods=['GET','DELETE','PUT','POST'])
def admin_equipment():
    if request.method == 'GET':
        total_data = 'Just prevent from Error' #Get quipment [equipmentID,Title_eq, Status , img ,sid,department,year,expiredate ]
        results = [
                {
                    "equipmentID": 1,
                    "Title_eq": 1,
                    "Status": 1,
                    "img": 1,
                    "sid": 1,
                    "department": 1,
                    "year": 1,
                    "expiredate": 1,
                } for each_data in total_data]
        return {"data": results}
    if request.method == 'DELETE':
        equipmentID = request.form['equipmentID']
        Title_eq = request.form['Title_eq']
        Status = request.form['Status']
        img = request.form['img']
        sid = request.form['sid']
        department = request.form['department']
        year = request.form['year']
        cursor = mysql.connection.cursor()
        #DELETE equipment 
        cursor.execute(''' DELETE FROM jiwjiw WHERE id = (%s)''',(equipmentID))
        mysql.connection.commit()
        cursor.close()
        return f"delete equipment success!!"
    if request.method == 'PUT':  
        EQ_Title = request.form['EQ_Title']
        EQ_ID = request.form['EQ_ID']
        Status = request.form['Status']
        Borrow_date = request.form['Borrow_date']
        Return_date = request.form['Return_date']
        cursor = mysql.connection.cursor()
        #edit equipment VVV
        cursor.execute(''' UPDATE FROM jiwjiw WHERE id = (%s)''',(EQ_ID))
        mysql.connection.commit()
        cursor.close()
        return f"update status equipment success!!"
    if request.method == 'POST':
        EQ_Title = request.form['EQ_Title']
        EQ_ID = request.form['EQ_ID']
        Img = request.form['Img']
        cursor = mysql.connection.cursor()
        #INSERT EQUIPMENT
        cursor.execute(''' INSERT INTO jiwjiw ''')
        mysql.connection.commit()
        cursor.close()
        return f"update status equipment success!!"
    
@app.route('/admin-request',methods=['GET','PUT','POST','DELETE'])
def request_equipment():
    if request.method == 'GET':
        total_data = 'Just prevent from Error' #Get equipment that student's request [ID,Title ,std_id,EQID , img,expiredate ]
        results = [
                {
                    "ID": 1,
                    "Title": 1,
                    "std_id": 1,
                    "EQID": 1,
                    "img": 1,
                    "expiredate": 1,
                } for each_data in total_data]
        return {"data": results}
    if request.method == 'PUT':
        ID = request.form['ID']
        Title = request.form['Title']
        std_idEQ = request.form['std_idEQ']
        img = request.form['img']
        expiredate = request.form['expiredate']
        cursor = mysql.connection.cursor()
        #UPDATE euipment  ??????
        cursor.execute(''' UPDATE FROM jiwjiw WHERE id = (%s)''',(ID))
        mysql.connection.commit()
        cursor.close()
        return f"update status equipment success!!"
    if request.method == 'POST': 
        EQ_ID = request.form['EQ_ID']
        Tittle_EQ = request.form['Tittle_EQ']
        Status = request.form['Status']
        cursor = mysql.connection.cursor()
        #INSERT status == notav VVV
        cursor.execute(''' UPDATE FROM jiwjiw WHERE id = (%s)''',(EQ_ID))
        mysql.connection.commit()
        cursor.close()
        return f"update status equipment success!!"
    if request.method == 'DELETE':
        EQ_ID = request.form['EQ_ID']
        Tittle_EQ = request.form['Tittle_EQ']
        Status = request.form['Status']
        Expireddate = request.form['Expireddate']
        Returndate = request.form['Returndate']
        cursor = mysql.connection.cursor()
        #DELETE status == av VVV
        cursor.execute(''' UPDATE FROM jiwjiw WHERE id = (%s)''',(EQ_ID))
        mysql.connection.commit()
        cursor.close()
        return f"update status equipment success!!"

def find_account(user, password):
    print(user, password)
    #หา user ที่มี user_id ตรงกับ input โดยเรียกข้อมูล id และ รหัส
    if user in mock_users_data:
        if check_password_hash(mock_users_data[user]["password"], password):
            return {"user_id":user, "role":"user"}
    elif user in mock_admins_data:
        if check_password_hash(mock_admins_data[user]["password"], password):
            return {"user_id":user, "role":"admin"}

@app.after_request
def refresh_expiring_jwts(response):
    try:
        exp_timestamp = get_jwt()["exp"]
        now = datetime.now(timezone.utc)
        target_timestamp = datetime.timestamp(now + timedelta(minutes=30))
        if target_timestamp > exp_timestamp:
            access_token = create_access_token(identity=get_jwt_identity())
            data = response.get_json()
            if type(data) is dict:
                data["access_token"] = access_token 
                response.data = json.dumps(data)
        return response
    except (RuntimeError, KeyError):
        # Case where there is not a valid JWT. Just return the original respone
        return response

@app.route('/login', methods=["POST"])
def login():
    if request.method == "POST" and "sid" in request.form and "password" in request.form:
        user = request.form["sid"]
        password = request.form["password"]
        account = find_account(user, password)
        if account:
            userinfo = {}
            userinfo["sid"] = account["user_id"]
            userinfo["role"] = account["role"]
            access_token = create_access_token(identity=userinfo)
            return {"access_token":access_token, "role":userinfo["role"]}
    return {"msg":"Wrong user ID or password."}

@app.route('/register', methods=['POST'])
def register():
    name = request.form['name']
    lastname = request.form['surname']
    major = request.form['depart']
    year = request.form['year']
    student_id = request.form['sid']
    if name == "" or lastname == "" or major == "" or year == "" \
        or student_id == "" or request.form['password'] == "":
        return {"msg":"There are some fields that you have left blank."}
    password = generate_password_hash(request.form['password'])
    #ดึง user_id และ admin_id ทั้งหมด เพื่อหาว่าลงทะเบียนไปแล้วหรือไม่
    if student_id not in mock_users_data and student_id not in mock_admins_data:
        #เพิ่ม user คนใหม่
        mock_users_data[student_id] = {"name":name,"lastname":lastname,"major":major,"year":year,"password":password}
        userinfo = {"sid":student_id, "role":"user"}
        access_token = create_access_token(identity=userinfo)
        return {"access_token":access_token, "role":"user"}
    else:
        return {"msg":"This id is already registered."}

@app.route('/equipments', methods=["GET"])
def equipments_lists():
    response = []
    count = 0
    #ดึงข้อมูล equipment ทั้งหมด และข้อมูล ID, Major/depart, ปี ของผู้ที่ยืมอยู่ ถ้ามี
    for eqm in mock_equipment_data:
        count += 1
        eqm_id = eqm[0]
        print(len(eqm_id))
        sid = ""
        s_dep = ""
        s_year = ""
        for borrow in mock_borrow_data:
            image_name = os.path.abspath(os.path.join(image_folder,eqm[6]))
            with open(image_name, 'rb') as image_file:
                encoded_image = base64.b64encode(image_file.read()).decode('utf-8')
            if borrow[0] == eqm_id:
                sid = borrow[1]
                s_dep = mock_users_data[sid]["major"]
                s_year = mock_users_data[sid]["year"]
                break

        response.append(    {   
                                "id":eqm_id,
                                "title":eqm[1],
                                "type":eqm[2],
                                "category":eqm[3],
                                "status": eqm[4],
                                "location": eqm[5],
                                "department":s_dep,
                                "year":s_year,
                                "studentid": sid,
                                "image": encoded_image
                            })
    return jsonify(response)

@app.route('/<string:sid>/borrowing', methods=["GET"])
@jwt_required()
def borrowed_equipments(sid):
    try:
        decoded = get_jwt()
        if "sub" in decoded:
            if decoded["sub"]["sid"] == sid and decoded["sub"]["role"] == "user":
                response = []
                #ดึงข้อมูล equipment ทุก equipment ที่ user (ID) คนนี้ยืม
                for borrow in mock_borrow_data:
                    if borrow[1] == sid:
                        for eqm in mock_equipment_data:
                            if eqm[0] == borrow[0]:
                                image_name = os.path.abspath(os.path.join(image_folder,eqm[6]))
                                with open(image_name, 'rb') as image_file:
                                    encoded_image = base64.b64encode(image_file.read()).decode('utf-8')
                                response.append( { "id":eqm[0],
                                                    "title":eqm[1],
                                                    "type":eqm[2],
                                                    "category":eqm[3],
                                                    "status": eqm[4],
                                                    "location": eqm[5],
                                                    "img":encoded_image
                                                    })
                                break
                return jsonify(response)
            return {"msg":"Wrong User"}, 404
        return {"msg":"Unauthorized access"}, 401
    except:
        return {"msg": "Internal server error"}, 500

"""@app.route('/<string:admin_id>/admin_equipment', methods=["GET", "POST", "PUT"])
@jwt_required()
def equipment_detail(admin_id):
    if request.method == "GET":
        pass
    elif request.method == "POST":
        pass
    elif request.method == "PUT":
        pass"""

@app.route("/<string:admin_id>/admin_equipment", methods=["GET"])
@jwt_required()
def admin_eqm_detail(admin_id):
    try:
        decoded = get_jwt()
        if "sub" in decoded:
            if decoded["sub"]["sid"] == admin_id and decoded["sub"]["role"] == "admin":
                response = []
        count = 0
        #ดึงข้อมูล equipment ทั้งหมด และข้อมูล ID, Major/depart, ปี ของผู้ที่ยืมอยู่ ถ้ามี และวันที่ให้ยืม กับวันที่คืน ถ้ามี
        for eqm in mock_equipment_data:
            count += 1
            eqm_id = eqm[0]
            print(len(eqm_id))
            sid = ""
            s_dep = ""
            s_year = ""
            borrow_date = ""
            return_date = ""
            for borrow in mock_borrow_data:
                #รูป
                image_name = os.path.abspath(os.path.join(image_folder,eqm[6]))
                with open(image_name, 'rb') as image_file:
                    encoded_image = base64.b64encode(image_file.read()).decode('utf-8')
                #-------------------------------------------------------------------------
                if borrow[0] == eqm_id:
                    sid = borrow[1]
                    s_dep = mock_users_data[sid]["major"]
                    s_year = mock_users_data[sid]["year"]
                    borrow_date = borrow[2]
                    return_date = borrow[3]
                    break

            response.append(    {   
                                    "id":eqm_id,
                                    "title":eqm[1],
                                    "type":eqm[2],
                                    "category":eqm[3],
                                    "status": eqm[4],
                                    "location": eqm[5],
                                    "department":s_dep,
                                    "year":s_year,
                                    "studentid": sid,
                                    "image": encoded_image,
                                    "borrow_date":borrow_date,
                                    "return_date":return_date
                                })
        return jsonify(response)

    except:
        return {"msg": "Internal server error"}, 500

@app.route("/<string:admin_id>/admin_equipment/delete/<string:eqm_id>", methods=["DELETE"])
@jwt_required()
def delete_equipment(admin_id, eqm_id):
    try:
        decoded = get_jwt()
        if "sub" in decoded:
            if decoded["sub"]["sid"] == admin_id and decoded["sub"]["role"] == "admin":
                #ลบการยืม eqm นี้ออกจาก database
                #ลบ eqm นี้ออกจาก database
                target_eqm = None
                for eqm in mock_equipment_data:
                    if eqm[0] == eqm_id:
                        target_eqm = eqm
                        break
                if target_eqm:
                    copy_borrow_data = mock_borrow_data.copy()  
                    for borrow in copy_borrow_data:
                        if borrow[0] == target_eqm[0]:
                            mock_borrow_data.remove(borrow)
                    del copy_borrow_data
                    mock_equipment_data.remove(target_eqm)
                #----------------------------------------------------------------------------
                    #เจอ eqm นั้น
                    return {"msg":f"Equipment of id {eqm_id} is deleted successfully."}
                else:
                    #ไม่เจอ eqm นั้น
                    return {"msg":f"Equipment of id {eqm_id} doesn't exists."}
            return {"msg": "Unauthorized access"} , 401
    except:
        return {"msg": "Internal server error"}, 500
                        

@app.route('/<string:admin_id>/admin_control/add_admin', methods=["POST"])
@jwt_required()
def add_admin_member(admin_id):
    try:
        decoded = get_jwt()
        if "sub" in decoded:
            if decoded["sub"]["sid"] == admin_id and decoded["sub"]["role"] == "admin":
                name = request.form['name']
                lastname = request.form['surname']
                depart = request.form['depart']
                newadmin_id = request.form['sid']
                password = generate_password_hash(request.form['password'])
                #ดึง user_id และ admin_id ทั้งหมด เพื่อหาว่าลงทะเบียนไปแล้วหรือไม่
                if newadmin_id not in mock_admins_data and newadmin_id not in mock_users_data:
                    #เพิ่ม admin คนใหม่
                    mock_admins_data[newadmin_id] = {"name":name,"lastname":lastname,"depart":depart,"password":password}

                    #ลงทะเบียนสำเร็จ
                    return {"msg":f"Admin {newadmin_id} is added successfully"}
                #ลงทะเบียนไปแล้ว
                return {"msg":"Already registered"}
            return {"msg": "Unauthorized access"} , 401
    except:
        return {"msg": "Internal server error"}, 500

@app.route("/<string:admin_id>/admin_control/delete_admin/<string:delete_id>", methods=["DELETE"])
@jwt_required()
def delete_admin(admin_id, delete_id):
    try:
        decoded = get_jwt()
        if "sub" in decoded:
            if decoded["sub"]["sid"] == admin_id and decoded["sub"]["role"] == "admin":
                #ลบ Admin ที่มี id ตรงกับ delete_id
                if delete_id in mock_admins_data:
                    del mock_admins_data[delete_id]
                    return {"msg":f"Deletion of admin {delete_id} is successful."}
                return {"msg":f"No admin {delete_id} exists."}
            return {"msg":"Unauthorized address"}, 403
        return {"msg":"Unauthorized address"}, 403
    except:
        return {"msg": "Internal server error"}, 500

@app.route("/logout", methods=["POST"])
def logout():
    response = jsonify({"msg": "logout successful"})
    unset_jwt_cookies(response)
    return response

if __name__ == "__main__":
    app.run(host='localhost', debug = True, port=5000)