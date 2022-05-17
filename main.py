import random
from flask import Flask, render_template, request, redirect, session
import mysql.connector
from datetime import date

app = Flask('app')
app.secret_key = "overflow"


mydb = mysql.connector.connect(
  host="overflow-cuz-we-re-stacked.cssvb03ow4mi.us-east-1.rds.amazonaws.com",
  user="admin",
  password="alaimolibboncarpenter",
  database="university"
)

@app.route('/')
def dashboard():
  return render_template("dashboard.html")

@app.route('/app-landing')
def applanding():
  return render_template("landing.html")

@app.route('/login', methods=['GET', 'POST'])
def login():
  error = False
  connection = mydb.cursor(dictionary=True)

  if request.method == 'POST':
    r_username = request.form['field_name']
    r_password = request.form['field_password']

    connection.execute("SELECT * FROM users WHERE username=%s AND password=%s", (r_username, r_password,))
    login = connection.fetchone()

    if login is None:
      error = True
      return render_template("regs_login.html", error = error)
    else:
      error = False
      # session["username"] = r_username
      session["name"] = login["fname"] + " " + login["lname"]
      session["user_type"] = login["utype"]
      session['user_id'] = login['user_id']
      return redirect('/home')    

  return render_template("regs_login.html", error = error)

@app.route('/home', methods=['GET', 'POST'])
def home():
  if 'user_type' not in session:
    return redirect ('/not_allowed')
  else:
    # Display the correct information for a logged in user 
    connection = mydb.cursor(dictionary=True, buffered=True)

    # system admin list of users
    if session['user_type'] == "sys_admin":
      connection.execute("SELECT * FROM users")
      users=connection.fetchall()

      return render_template("home.html", uid = session['user_id'], users = users)

    # applicant application status
    if session['user_type'] == "applicant":
      connection.execute("SELECT * FROM applications JOIN users ON applications.app_id=users.user_id WHERE app_id=%s", (session['user_id'],))
      applicant = connection.fetchone()
      # print(applicant)
      
      connection.execute("SELECT count(*) FROM rec_letters WHERE app_id=%s", (session['user_id'],))
      count = connection.fetchall()

      num = count[0].get("count(*)")
      recs=False
      if num != 0:
        recs = True

      # print("there are recs: " + str(recs))
      # print("there is a transcript: " + applicant['transcript'])

      if applicant['transcript'] == 'N' and recs == True:
        return render_template("home.html", uid = session['user_id'], app_stat=applicant['app_stat'], msg="INCOMPLETE - Missing transcript.")
      elif applicant['transcript'] == 'Y' and recs == False:
        return render_template("home.html", uid = session['user_id'], app_stat=applicant['app_stat'], msg="INCOMPLETE - Missing a letter of recommendation.")
      elif applicant['transcript'] == 'Y' and recs == True and applicant['decision'] == 'NA':
        # print("app is complete")
        connection.execute("UPDATE applications SET app_stat=%s WHERE app_id=%s",("COMPLETE",session['user_id']))
        return render_template("home.html", uid = session['user_id'], app_stat=applicant['app_stat'], msg="COMPLETE - Currently in review.")
      
      if applicant['decision'] != 'NA':
        if applicant['decision'] == 'Reject':
          decision = "Your application for admission has been denied :("
        else:
          decision = "Congratulations you have been admitted! You will receive your formal letter of acceptance in the mail."
        return render_template("home.html", uid = session['user_id'], app_stat=applicant['app_stat'], msg=decision)

      return render_template("home.html", uid = session['user_id'], app_stat=applicant['app_stat'], msg="INCOMPLETE - Missing transcript and a letter of recommendation.")

    if session['user_type'] == "student":
      connection.execute("SELECT program FROM students WHERE s_id=%s", (int(session['user_id']), ))
      student = connection.fetchone()
      return render_template("home.html", student = student)

    # reviewers
    if session["user_type"] == "fac_rev" or session["user_type"] == "cac":
      connection.execute("SELECT * FROM applications JOIN users ON applications.app_id=users.user_id WHERE app_stat='COMPLETE' AND decision='NA' ORDER BY users.lname ASC ")
      applicants = connection.fetchall()
      # print(applicants)
      return render_template("home.html", applicants = applicants)

    #faculty advisor
    if session["user_type"] == "fac_adv":
      cursor = mydb.cursor(dictionary=True)
      cursor.execute("SELECT * FROM users JOIN students ON users.user_id = students.s_id JOIN advises ON users.user_id=advises.s_id WHERE advises.adv_id = %s", (session['user_id'],))
      students= cursor.fetchall()
      # print(students)
      return render_template("home.html", students = students)

    return render_template("home.html", uid=session['user_id'])


@app.route('/logout', methods=['GET', 'POST'])
def logout():
  # Log the user out and redirect them to the login page
  session.clear()
  return redirect('/')

@app.route('/signup', methods=['GET', 'POST'])
def signup():
  # error = False

  if request.method == "POST":
    uname = request.form["signup_uname"]
    password=request.form["signup_pass"]
    utype=request.form["field_utype"]
    fname=request.form["signup_fname"]
    lname=request.form["signup_lname"]

    connection = mydb.cursor(dictionary=True) 
    connection.execute("SELECT * from users")
    users = connection.fetchall()

    for user in users:
      if uname == user["username"]:
        # error = True
        return render_template("signup.html", error="A user with that username already exists. Please log in or try again.")

    connection.execute("SELECT * from users")
    ids = connection.fetchall()

    max = 10000001
    for id in ids:
      if int(id["user_id"]) > max:
        max = id["user_id"]

    max = max+1

    connection.execute("INSERT INTO users (user_id, username, password, utype, fname, lname) VALUES (%s, %s, %s, %s, %s, %s)", (max, uname, password, utype, fname, lname))
    mydb.commit()

    if utype == "student":
      return redirect('/new-stud/' + str(max))
    
    if 'user_type' in session:
      if session['user_type'] == 'sys_admin':
        return redirect("/home")

    connection.execute("SELECT user_id, utype, fname, lname FROM users WHERE user_id=%s", (max,))
    user=connection.fetchone()
    session["name"] = user["fname"] + " " + user["lname"]
    session["user_type"] = user["utype"]
    session['user_id'] = user['user_id']

    return redirect("/home")


  return render_template("signup.html")

@app.route('/app-form/<uid>', methods=['GET', 'POST'])
def appform(uid):
  # Display the correct information for a logged in user 
  if request.method == 'POST':
    app_deg=request.form['field_appdeg']
    interest=request.form['field_int']
    work_ex=request.form['field_exp']
    sem=request.form['field_sem']
    year=request.form['field_year']
    # app status
    # decision
    
    # uid
    greS=request.form['field_grescore']
    greV=request.form['field_grev']
    greQ=request.form['field_greq']
    exyear=request.form['field_exyear']
    greSub=request.form['field_sub']
    toefl=request.form['field_toefl']
    tDate=request.form['field_toefldate']

    # uid
    degyear=request.form['field_degyear']
    degpa=request.form['field_degpa']
    deguni=request.form['field_deguni']
    degmajor=request.form['field_degmajor']
    # prior_deg=request.form.getlist('field_priordeg') # BA/BS
    
    # uid
    msyear=request.form['field_msyear']
    msgpa=request.form['field_msgpa']
    msuni=request.form['field_msuni']
    msmajor=request.form['field_msmajor']
    prior_ms=request.form.getlist('field_priorms') # MS
  
    connection = mydb.cursor(dictionary=True)
    connection.execute("INSERT INTO applications (app_id, deg_sought, area_of_int, work_exp, app_sem, app_year, transcript, app_stat, decision) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)", (uid, app_deg, interest, work_ex, sem, year, 'N', "INCOMPLETE", "NA"))
    connection.execute("INSERT INTO tests (app_id, gre_score, gre_v, gre_q, gre_year, gre_sub, toefl, toefl_date) VALUES (%s, %s, %s, %s, %s, %s, %s, %s)", (uid, greS, greV, greQ, exyear, greSub, toefl, tDate))
    # if prior_deg:
      # print("we got here!")
    connection.execute("INSERT INTO degrees (deg_id, app_id, deg_year, uni, gpa, major) VALUES (%s, %s, %s, %s, %s, %s)", ("BA/BS", uid, degyear, deguni, degpa, degmajor))
    if prior_ms:
      connection.execute("INSERT INTO degrees (uid, deg_year, gpa, uni, major, deg_id) VALUES (%s, %s, %s, %s, %s, %s)", ("MS", uid, msyear, msuni, msgpa, msmajor))
    connection.execute("UPDATE users SET utype='applicant' WHERE user_id=%s", (uid,))
    mydb.commit()
    session['user_type'] = 'applicant'
    return render_template("success.html")
  return render_template("app_form.html", uid=uid)

@app.route('/rec_request/<uid>', methods=['GET', 'POST'])
def rec_request(uid):
  if request.method == "POST":
    wname = request.form["rec_wname"]
    wemail = request.form["rec_wemail"]
    wtitle = request.form["rec_wtitle"]

    connection = mydb.cursor(dictionary=True, buffered = True) 
    # connection.execute("SELECT * FROM users WHERE user_id=%s", (uid,))
    # student=connection.fetchone()
    from datetime import date
    today = date.today()

    from datetime import datetime
    date = datetime.now()  


    connection.execute("INSERT INTO rec_letters (app_id, wname, wemail, wtitle, date, letter, rating, generic, credibility) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)",(uid, wname, wemail, wtitle, date, "empty", "1", "X", "X")) 
    
    mydb.commit()
    return render_template('rec_letter_email.html', title=wtitle, name=wname, student=session["name"])

  # need to change return
  return render_template('rec_letter_request.html', uid=uid)

@app.route('/rec_submit', methods=['GET', 'POST'])
def rec_submit():

  if request.method == 'POST':
    letter = request.form["rec_textarea"]
    # print(letter)
    name = request.form["rec_submit_name"]
    connection = mydb.cursor(dictionary=True)
    connection.execute("UPDATE rec_letters set letter=%s WHERE wname=%s", (letter, name))
    mydb.commit()
    return redirect("/home")

  return render_template("rec_letter_submit.html")

@app.route('/app-review/<uid>', methods=['GET', 'POST'])
def revform(uid):

  if 'user_type' not in session:
    return redirect ('/not_allowed')
  if session['user_type'] == 'grad_sec' or session['user_type'] == 'cac' or session['user_type'] == 'fac_rev':
    recs = False
    connection = mydb.cursor(dictionary=True)
    connection.execute("SELECT * FROM users WHERE user_id=%s", (uid,))
    users = connection.fetchall()
    connection.execute("SELECT * FROM applications WHERE app_id=%s", (uid,))
    applications = connection.fetchall()
    connection.execute("SELECT * FROM tests WHERE app_id=%s", (uid,))
    tests = connection.fetchall()
    connection.execute("SELECT * FROM degrees WHERE app_id=%s", (uid,))
    degrees = connection.fetchall()
    
    connection.execute("SELECT count(*) FROM rec_letters WHERE app_id=%s", (uid,))
    let = connection.fetchall()
    count_let = let[0].get("count(*)")

    if count_let != 0:
      recs=True
    
    connection.execute("SELECT * FROM rec_letters WHERE app_id=%s", (uid,))
    letters = connection.fetchall()
    
    final_dec=False
    connection.execute("SELECT count(*) FROM reviews WHERE app_id=%s", (uid,))
    count = connection.fetchall()
    num = count[0].get("count(*)")

    msg=False

    if num >= 1:
      final_dec=True
      connection.execute("SELECT * FROM reviews WHERE app_id=%s", (uid,))
      reviews = connection.fetchall()
    else:
      msg=True
      reviews = "There are currently no reviews"

    if request.method == "POST":
      # for the cac and grad sec if there is at least 1 review already
      if (session["user_type"] == "cac" or session["user_type"] == "grad_sec") and (final_dec == True):
        advisor = request.form["rec_adv_field"]
        final_dec = request.form["final_decision"]
        connection.execute("UPDATE applications SET decision=%s WHERE app_id=%s", (final_dec, uid))
        connection.execute("UPDATE reviews SET final_dec=%s, rec_advisor=%s WHERE rev_id=%s AND app_id=%s", (final_dec, advisor, session['user_id'], uid))
        mydb.commit()
        return redirect('/home')
      # gas review form info
      gas_rev = request.form["gas_review"]
      deficiency = request.form["deficiency_field"]
      comments = request.form["rev_comment_field"]
      # if gas_rev == "Reject":
      reasons = request.form["reject_reason"]
      # if num == 0:
      connection.execute("INSERT INTO reviews (rev_id, app_id, gas_rev, course_def, comments, final_dec, reason, rec_advisor) VALUES (%s, %s, %s, %s, %s, %s, %s, %s)", (session['user_id'], uid, gas_rev, deficiency, comments, "not yet made", reasons, "not yet decided"))
      mydb.commit()

      return redirect('/home')
    # print(rev)
    for app in applications:
      if app['decision'] != 'NA':
        return render_template("review_form.html", users=users, applications=applications, tests=tests, degrees=degrees, uid=uid, letters=letters, recs=recs, reviews=reviews, msg=msg, final_dec=final_dec, edit=False)
    return render_template("review_form.html", users=users, applications=applications, tests=tests, degrees=degrees, uid=uid, letters=letters, recs=recs, reviews=reviews, msg=msg, final_dec=final_dec, edit=True)
  return redirect ('/not_allowed')

@app.route('/user-info/<uid>', methods=['GET', 'POST'])
def user_info(uid):
  connection = mydb.cursor(buffered=True, dictionary=True)
  connection.execute("SELECT * FROM users WHERE user_id=%s", (uid,))
  user=connection.fetchone()
  utype=request.args.get('field_utype')

  if request.method == 'POST':
    
    uname=request.form['field_uname']
    password=request.form['field_pass']
    fname=request.form['field_fname']
    lname=request.form['field_lname']
    email=request.form['field_email']
    prons=request.form['field_prons']
    phone=request.form['field_phone']
    dob=request.form['field_dob']
    st_add=request.form['field_stadd']
    city=request.form['field_city']
    state=request.form['field_state']
    zip=request.form['field_zip']
    # ssn=request.form['field_ssn']

    connection.execute("UPDATE users SET username=%s, password=%s, utype=%s, fname=%s, lname=%s, pronouns=%s, dob=%s, phone=%s, email=%s, street_add=%s, city=%s, state=%s, zipcode=%s WHERE user_id=%s", (uname, password, utype, fname, lname, prons, dob, phone, email, st_add, city, state, zip, uid))
    mydb.commit()
  
    return redirect('/home')

  return render_template("user_info.html", user=user)

@app.route('/update-transcript/<uid>', methods=['GET', 'POST'])
def updatetranscript(uid):
  connection = mydb.cursor(dictionary=True)
  status = request.form["updatetranscript"]
  if status == "Y":
    # print("transcript received")
    connection.execute("UPDATE applications SET transcript=%s WHERE app_id=%s", ('Y', uid))
    mydb.commit()
    connection.execute("SELECT count(*) FROM rec_letters WHERE app_id=%s", (uid,))
    count = connection.fetchall()

    num = count[0].get("count(*)")
    recs=False
    if num != 0:
      recs = True

    # print("update-transcript --- there are recs: " + str(recs))
    # print("update-transcript --- there is a transcript: " + status)
    if recs == True:
      # print("update --- app is complete")
      connection.execute("UPDATE applications SET app_stat=%s WHERE app_id=%s",("COMPLETE", uid))
      mydb.commit()
    return redirect("/home")
  
  connection.execute("UPDATE applications SET transcript=%s WHERE app_id=%s", ('N', uid))
  mydb.commit()
  # connection.execute("SELECT transcript FROM applications WHERE app_id=%s", (uid,))
  # applicant=connection.fetchone()
  return redirect("/home")

@app.route('/displayletter/<recid>', methods=['GET', 'POST'])
def displayletter(recid):
  # could be rec_id
  connection = mydb.cursor(dictionary=True)
  connection.execute("SELECT * FROM rec_letters WHERE rec_id=%s", (recid,))
  letter = connection.fetchone()
  if request.method == 'POST':
    rating = request.form["reviewrating"]
    generic = request.form["reviewgeneric"]
    credible = request.form["reviewcredible"]
    # insert into updated schema
    connection.execute("UPDATE rec_letters SET rating=%s, generic=%s, credibility=%s WHERE rec_id=%s", (rating, generic, credible, recid))
    mydb.commit()
    # print(letter['app_id'])
    return redirect("/app-review/" + str(letter['app_id']))

  return render_template("rec_letter_display.html", letter=letter)

@app.route('/search', methods=['POST'])
def search():
  if request.method == 'POST':
    search = request.form['search']
    connection = mydb.cursor(dictionary=True, buffered=True)
    connection.execute("SELECT * FROM users WHERE fname LIKE %s OR lname LIKE %s ", ('%'+search+'%', '%'+search+'%'))
    # connection.execute("SELECT * FROM users WHERE user_id=%s", (search,))
    user = connection.fetchone()
    if session['user_type'] == 'sys_admin':
      if user == None:
        return render_template("user_info.html", user=user)
      else:
        return render_template("user_info.html", user=user)
    elif session['user_type'] == 'grad_sec':
      if user == None:
        return redirect('/gs_apprev')
      else:
        return redirect("/app-review/" + str(user['user_id']))
    elif session['user_type'] == 'fac_rev':
      if user != None:
        return redirect("/app-review/" + str(user['user_id']))
      else:
        return redirect("/home")
    elif session['user_type'] == 'cac':
      if user != None:
        return redirect("/app-review/" + str(user['user_id']))
      else:
        return redirect("/home")
  
  return render_template("home.html")

@app.route('/app-comp/<uid>', methods=['GET', 'POST'])
def appcomp(uid):
  if 'user_type' not in session:
    return redirect ('/not_allowed')
  if session['user_type'] != 'grad_sec':
    return redirect ('/not_allowed')
  connection = mydb.cursor(dictionary=True)
  connection.execute("SELECT * FROM users WHERE user_id=%s", (uid,))
  user = connection.fetchone()
  connection.execute("SELECT * FROM applications WHERE app_id=%s", (uid,))
  application = connection.fetchone()
  # connection.execute("SELECT count(*) FROM rec_letters WHERE app_id=%s", (uid,))
  # count = connection.fetchall()

  # num = count[0].get("count(*)")
  # recs=False
  # if num != 0:
  #   recs = True

  # # print("app-comp --- there are recs: " + str(recs))
  # # print("app-comp --- there is a transcript: " + application['transcript'])
  # if application['transcript'] == 'Y' and recs == True:
  #   print("app-comp --- app is complete")
  #   connection.execute("UPDATE applications SET app_stat=%s",("COMPLETE",))
  # print("app-comp: " + application['app_stat'])

  return render_template("app_comp.html", user=user, application=application, uid=uid)

#### ADS CODE STARTS HERE
def credits_calc(s_id):
  cursor = mydb.cursor(dictionary=True)
  cursor.execute("SELECT * FROM enrolled_in JOIN courses ON enrolled_in.course_id = courses.course_id WHERE student_id = %s", (int(s_id),))
  courses = cursor.fetchall()
  cursor.execute("SELECT * FROM students WHERE s_id = %s", (int(s_id), ))
  student = cursor.fetchone()
  results = {}
  if student != None:
    results['degree'] = student['program']
  results['credits'] = 0         #store total amount of credits
  results['cs_credits'] = 0      #stores credits specifically in cs courses (phd)
  results['gpa'] = 0.0           #stores gpa
  results['b_below'] = 0         #counter of classes below a b
  results['core_req'] = 0        #counter of classes that meet requirements for CS(ms)
  results['outside_courses'] = 0
  results['outside_credits'] = 0
  results['courses'] = courses
  # results['degree'] = student['program']

  for i in courses:
    results['credits'] += i['credits']
    if i['grade'] == 'A':
      results['gpa'] += 4
    elif i['grade'] == 'A-':
      results['gpa'] += 3.7
    elif i['grade'] == 'B+':
      results['gpa'] += 3.3
    elif i['grade'] == 'B':
      results['gpa'] += 3
    elif i['grade'] == 'B-':
      results['gpa'] += 2.7
      results['b_below'] +=1
    elif i['grade'] == 'C+':
      results['gpa'] += 2.3
      results['b_below'] +=1
    elif i['grade'] == 'C':
      results['gpa'] += 2
      results['b_below'] +=1
    elif i['grade'] == 'C-':
      results['gpa'] += 1.7
      results['b_below']+=1
    elif i['grade'] == 'D+':
      results['gpa'] += 1.3
      results['b_below'] +=1
    elif i['grade'] == 'D':
      results['gpa'] += 1
      results['b_below'] +=1
    elif i['grade'] == 'D-':
      results['gpa'] += .7
      results['b_below'] +=1
    elif i['grade'] == 'F':
      results['gpa'] += 0
      results['b_below'] +=1

    cursor.execute("SELECT * FROM courses WHERE course_id = %s", (i['course_id'],))
    course_info = cursor.fetchone()

    if course_info['dept'] == 'CSCI':
      results['cs_credits'] += course_info['credits']
      if course_info['cnum'] == 6212 or 6221 or 6461:
        results['core_req'] += 1

    elif course_info['dept'] != 'CSCI':
      results['outside_courses'] += 1
      if student['program'] == "MS":
        if results['outside_courses'] <= 2:
          results['outside_credits'] += course_info['credits']

  if len(courses) != 0:
    results['gpa'] = results['gpa']/len(courses)
    results['gpa'] = "{:.2f}".format(results['gpa'])

  return results

@app.route('/form1', methods=['GET', 'POST'])
def form1():
  if 'user_type' not in session:
    return redirect ('/not_allowed')
  if session['user_type'] != 'student':
    return redirect('/not_allowed')

  cursor = mydb.cursor(dictionary=True, buffered=True)

  #check to see if it already submitted
  cursor.execute("SELECT * FROM form_one WHERE s_id=%s", (int(session['user_id']),))
  form_check = cursor.fetchone()

  if form_check is not None:
    message = "You have already submitted your Form 1."
    return render_template("form1.html", message = message)
  else:
    max_length = 12 #used in html 
    form_courses = list()  #holds list of all courses id's from form 1
    other_courses = 0 #check to see if more than two classes are outside of CS department
    total_credits = 0
    cs_credits = 0
    error = 0
    core_classes = 0
    err_credits = ""
    err_cscredits = ""
    err_other_courses = ""
    err_core = ""
    err_degree = ""

    if request.method == 'POST':
      for i in range(12):
        degree = request.form['degree_type']
        course_sub = request.form['c_sub_' + str(i)]
        course_num = request.form['c_num_' + str(i)]

        if not course_num or not course_sub: #null check
          continue
        
        print(course_sub)
        cursor.execute("SELECT course_id, credits FROM courses WHERE dept = %s AND cnum = %s LIMIT 12", (course_sub, int(course_num)))
        form_cid = cursor.fetchone()
        if form_cid == None:
          continue 

        #sum total credit hours
        total_credits += form_cid['credits']

        if course_sub == 'CSCI':
          cs_credits += form_cid['credits']

        if form_cid not in form_courses: #checks multiples of the same course entered
          form_courses.append(form_cid['course_id'])

        #check for core classes
        if form_cid['course_id'] == 1 or form_cid['course_id'] == 2 or form_cid['course_id'] == 3:
          core_classes += 1

        #check for non CS classes
        if str(course_sub) != 'CSCI':
          other_courses += 1
      #endfor
    

      if degree == 'none':
        err_degree = " You did not select your degree type. "
        error += 1
  
      elif degree == 'MS':
        if total_credits < 30:
              err_credits = " You do not have enough credits. Please add more classes. "
              error += 1
        if other_courses > 2:
          err_other_courses =  " You have more than 2 courses listed outside of Computer Science. Please only select 2 or less non-computer science courses. "
          error += 1
        if core_classes != 3:
          err_core = " You are missing one or more of your core class requirements. They are CSCI 6212, CSCI 6221, and CSCI 6461."
          error += 1
      elif degree == 'PHD':
        if total_credits < 36:
              err_credits = " You do not have enough credits. Please add more classes. "
              error += 1
        if cs_credits < 30:
          err_cscredits = " You have less than 30 credits within computer science courses. Please add more computer science courses. "
          error += 1
      
      if error == 0: #if there are no errors with all the courses then insert into the database
        for course in form_courses:
          cursor.execute("INSERT INTO form_one (s_id, course_id) VALUES (%s, %s)", (int(session['user_id']), int(course)))
          cursor.execute("UPDATE students SET program = %s WHERE s_id = %s ", (degree, int(session['user_id'])))
          mydb.commit()
          
    return render_template("form1.html", form_courses = form_courses, max_length = max_length, err_degree = err_degree, err_credits = err_credits, err_core = err_core, err_other_courses = err_other_courses, err_cscredits = err_cscredits, error = error)

@app.route('/appgrad', methods=['GET', 'POST'])
def appgrad():
  if 'user_type' not in session:
    return redirect ('/not_allowed')
  if session['user_type'] != 'student':
    return redirect('/not_allowed')
  cursor = mydb.cursor(dictionary=True, buffered=True)
  cursor.execute("SELECT * FROM students WHERE s_id = %s", (int(session['user_id']), ))
  student = cursor.fetchone()
  calc = credits_calc(session['user_id'])

  cursor.execute("SELECT * FROM applies WHERE s_id = %s", (int(session['user_id']), ))
  grad_status = cursor.fetchone()
  if grad_status is not None:
    return render_template("congrats.html")
  
  cursor.execute("SELECT * FROM form_one WHERE s_id=%s", (int(session['user_id']),))
  form_check = cursor.fetchone()
 
  if calc['degree'] == "MS":
    if form_check is None:
      message = "You have not submitted your Form 1."
      return render_template("appgrad.html", courses=calc['courses'], credits=calc['credits'], gpa=calc['gpa'], message=message)
    if calc['cs_credits']+ calc['outside_credits'] < 30 or float(calc['gpa']) < 3.0 or calc['core_req'] < 3:
      if calc['cs_credits'] + calc['outside_credits'] < 30:
          message = "You need at least 30 credits in CS courses."
      elif calc['outside_course'] > 2:
        message = "You need less than 2 outside courses to apply for graduation."
      elif calc['core_req'] < 3:
        message = "You need to take CSCI 6212, CSCI 6221, and CSCI 6461 to apply for graduation."
      elif calc['gpa'] < 3.0:
          message = "your gpa needs to be at least 3.0 to apply for graduation"
      else:
        cursor.execute("INSERT INTO applies VALUES (%s, %s, %s)", (int(student['s_id']), float(calc['gpa']), calc['credits']))
        mydb.commit()
        return redirect('/home')
      return render_template("appgrad.html", courses=calc['courses'], credits=calc['credits'], gpa=calc['gpa'], message=message)
      
    return render_template("appgrad.html", courses=calc['courses'], credits=calc['credits'], gpa=calc['gpa'])

  if calc['degree'] == "PHD":
    if student['thesis'] == None:
      message = "You have not submitted your thesis."
      return render_template("appgrad.html", courses=calc['courses'], credits=calc['credits'], gpa=calc['gpa'], message=message)
    if student['approved'] == None:
      message = "Your thesis is pending approval."
      return render_template("appgrad.html", courses=calc['courses'], credits=calc['credits'], gpa=calc['gpa'], message=message)
    if form_check is None:
        message = "You have not submitted your Form 1."
        return render_template("appgrad.html", courses=calc['courses'], credits=calc['credits'], gpa=calc['gpa'], message=message)
    if calc['credits'] < 36 or float(calc['gpa']) < float(3.5) or calc['cs_credits'] < 30:
      if calc['credits'] < 36:
        message = "You need at least 36 credits to apply for graduation."
      elif calc['cs_credits'] < 30:
        message = "You need at least 30 CS credits to apply for graduation."
      elif calc['gpa'] < 3.5:
        message = "Your gpa needs to be at least 3.5 to apply for graduation."
      else:
        cursor.execute("INSERT INTO applies VALUES (%s, %s, %s)", (int(student['s_id']), float(calc['gpa']), calc['credits']))
        mydb.commit()
        return redirect('/home')
     
      return render_template("appgrad.html", courses=calc['courses'], credits=calc['credits'], gpa=calc['gpa'], message=message)

    return render_template("appgrad.html", courses=calc['courses'], credits=calc['credits'], gpa=calc['gpa'])

  message = "You have yet to take any courses"
  return render_template("appgrad.html", courses=calc['courses'], credits=calc['credits'], gpa=calc['gpa'], message = message)

@app.route('/congrats', methods=['GET', 'POST'])
def congrats():
  if request.method == 'POST':
    cursor = mydb.cursor(dictionary=True, buffered=True)
    calc = credits_calc(session['user_id'])
    cursor.execute("INSERT INTO applies (s_id, gpa, credits) VALUES (%s, %s, %s)", (int(session['user_id']),float(calc['gpa']),int(calc['credits'])))
    mydb.commit()
    return render_template("congrats.html")

@app.route('/personal_info/<user_id>', methods=['GET', 'POST'])
def personal_info(user_id):
  if int(session['user_id'])== int(user_id):
    cursor = mydb.cursor(dictionary=True)
    cursor.execute("SELECT * FROM users WHERE user_id = %s", (user_id,))
    user_info = cursor.fetchone()
    if request.method == 'POST':
      fname = request.form.get('fname')
      lname = request.form.get('lname')
      pronouns = request.form.get('pronouns') 
      dob = request.form.get('dob') 
      phone = request.form.get('phone') 
      email = request.form.get('email')
      street_add = request.form.get('street_add')
      city = request.form.get('city')
      state = request.form.get('state')
      zipcode = request.form.get('zipcode')
      ssn = request.form.get('ssn')

      # cursor.execute("SELECT * FROM users WHERE user_id = %s", (user_id,))
      # user_info = cursor.fetchone()

      if fname:
        cursor.execute("UPDATE users SET fname = %s WHERE user_id = %s", (fname, user_id))
      if lname:
        cursor.execute("UPDATE users SET lname = %s WHERE user_id = %s", (lname, user_id))
      if pronouns:
        cursor.execute("UPDATE users SET pronouns = %s WHERE user_id = %s", (pronouns, user_id))
      if dob:
        cursor.execute("UPDATE users SET dob = %s WHERE user_id = %s", (dob, user_id))
      if phone:
        cursor.execute("UPDATE users SET phone = %s WHERE user_id = %s", (phone, user_id))
      if email:
        cursor.execute("UPDATE users SET email = %s WHERE user_id = %s", (email, user_id))
      if street_add:
        cursor.execute("UPDATE users SET street_add = %s WHERE user_id = %s", (street_add, user_id))
      if city:
        cursor.execute("UPDATE users SET city = %s WHERE user_id = %s", (city, user_id))
      if state:
        cursor.execute("UPDATE users SET state = %s WHERE user_id = %s", (state, user_id))
      if zipcode:
        cursor.execute("UPDATE users SET zipcode = %s WHERE user_id = %s", (zipcode, user_id))
      if ssn:
        cursor.execute("UPDATE users SET zipcode = %s WHERE user_id = %s", (ssn, user_id))
      mydb.commit()
      # redirect('/home')
      cursor.execute("SELECT * FROM users WHERE user_id = %s", (user_id,))
      user_info = cursor.fetchone()
      route = '/personal_info/' + user_id
      redirect(route)
    return render_template("personal_info.html", user_info = user_info, user_id = user_id)
  else:
    return redirect ('/not_allowed')

@app.route('/view_form1/<s_id>', methods=['GET', 'POST'])
def view_form1(s_id):
  cursor = mydb.cursor(dictionary=True)
  cursor.execute("SELECT * FROM form_one JOIN courses ON form_one.course_id=courses.course_id WHERE s_id = %s", (s_id,))
  courses= cursor.fetchall()
  cursor.execute("SELECT fname, lname FROM users WHERE user_id =%s", (s_id,))
  name = cursor.fetchone()
  name = name['fname'] + ' ' + name['lname']
  return render_template("view_form1.html", name = name, courses = courses)

@app.route('/view_thesis/<s_id>', methods=['GET', 'POST'])
def view_thesis(s_id):
  if 'user_type' not in session:
    return redirect ('/not_allowed')
  if session['user_type'] != 'fac_adv':
    return redirect ('/not_allowed')
  cursor = mydb.cursor(dictionary=True)
  cursor.execute("SELECT * FROM students JOIN users ON s_id=user_id WHERE s_id = %s",(s_id,))
  student = cursor.fetchone()
  if student['thesis'] == None:
    message = "The student has not submitted their thesis. Please check back later."
    return render_template("view_thesis.html", student=student, message = message)
  elif student['approved'] == 'yes':
    message = "You have already approved this thesis."
    return render_template("view_thesis.html", student=student, message = message)
  return render_template("view_thesis.html", student=student)

@app.route('/thesis/<s_id>', methods=['GET', 'POST'])
def thesis(s_id):
  if 'user_type' not in session:
    return redirect ('/not_allowed')
  if session['user_type'] != 'student':
    return redirect('/not_allowed')
  cursor = mydb.cursor(dictionary=True)
  cursor.execute("SELECT thesis FROM students WHERE s_id=%s", (int(s_id), ))
  thesis_check = cursor.fetchone()
  print(thesis_check)

  if thesis_check['thesis'] != None:
    message = "You have already submitted your thesis. "
    return render_template("thesis.html", message = message)
  
  if request.method == 'POST':
    thesis = request.form['thesis']
    cursor.execute("UPDATE students SET thesis = %s WHERE s_id = %s", (thesis, int(s_id),))
    mydb.commit()
    return redirect('/home')
  return render_template("thesis.html")

@app.route('/approve/<s_id>', methods=['GET', 'POST'])
def approve_gradapps(s_id):
  cursor = mydb.cursor(dictionary=True)
  cursor.execute("SELECT program FROM students WHERE s_id=%s", (int(s_id), ))
  program = cursor.fetchone()
  year = '2022'

  if session['user_type'] == 'grad_sec':
    cursor.execute("UPDATE users SET utype=%s WHERE user_id=%s ", ("alumni", s_id))
    mydb.commit()
    cursor.execute("INSERT INTO alumni VALUES (%s, %s, %s)", (int(s_id), program["program"], year))
    mydb.commit()
    cursor.execute("DELETE FROM applies WHERE s_id=%s ", (s_id,))
    mydb.commit()
    cursor.execute("DELETE FROM advises WHERE s_id=%s ", (s_id,))
    mydb.commit()
    return redirect("/review_gradapps")
  elif session['user_type'] == 'fac_adv':
    cursor.execute("UPDATE students SET approved=%s WHERE s_id=%s", ('yes', s_id,))
    mydb.commit()
    return redirect("/home")

@app.route('/deny/<s_id>', methods=['GET', 'POST'])
def deny_gradapps(s_id):
  cursor = mydb.cursor(dictionary=True)
  mydb.commit()
  if session['user_type'] == 'grad sec':
    cursor.execute("DELETE FROM applies WHERE s_id=%s ", (s_id,))
    mydb.commit()
    return redirect("/home")
  elif session['user_type'] == 'fac_adv':
    cursor.execute("UPDATE students VALUES (%s) thesis = null WHERE s_id=%s", (s_id,))
    mydb.commit()
    return redirect("/home")
  return redirect("/review_gradapps")

@app.route('/assign_advisor', methods=['GET', 'POST'])
def assign_advisor():
  if 'user_type' not in session:
    return redirect ('/not_allowed')
  if session['user_type'] != 'grad_sec':
    return redirect ('/not_allowed')
  cursor = mydb.cursor(dictionary=True)
  cursor.execute("SELECT * FROM users WHERE utype LIKE 'student'")
  studs= cursor.fetchall()
  cursor.execute("SELECT * FROM users WHERE utype LIKE 'fac_adv'")
  advs = cursor.fetchall()
  if request.method == 'POST':
     s_id = int(request.form['student'])
     a_id = int(request.form['advisor'])
     cursor.execute("SELECT s_id FROM advises WHERE s_id=%s", (s_id,))
     assigned = cursor.fetchone()
     if assigned is not None:
       message = "This student already has an advisor. "
       return render_template("assign_advisor.html", students=studs, advisors=advs, message = message)
     else:
      cursor.execute("INSERT INTO advises VALUES ('%s', '%s');", (s_id, a_id))
      mydb.commit() 
      return redirect('/home')
  return render_template("assign_advisor.html", students=studs, advisors=advs)

@app.route('/review_gradapps', methods=['GET', 'POST'])
def review_gradapps():
  if 'user_type' not in session:
    return redirect ('/not_allowed')
  if session['user_type'] != 'grad_sec':
    return redirect ('/not_allowed')
  cursor = mydb.cursor(dictionary=True)
  cursor.execute("SELECT DISTINCT * FROM applies JOIN users ON s_id=user_id")
  applicants = cursor.fetchall()
  return render_template("review_gradapps.html", students=applicants)

@app.route('/students_data', methods=['GET', 'POST'])
def view_sdata():
  if 'user_type' not in session:
    return redirect ('/not_allowed')
  if session['user_type'] != 'grad_sec':
    return redirect ('/not_allowed')
  cursor = mydb.cursor(dictionary=True)
  cursor.execute("SELECT DISTINCT * FROM users LEFT JOIN advises ON user_id=advises.s_id Where utype LIKE 'student'")
  studs= cursor.fetchall()
  cursor.execute("SELECT DISTINCT * FROM users WHERE utype LIKE 'fac_adv'")
  advs = cursor.fetchall()
  return render_template("students_data.html", students=studs, advisors=advs)

@app.route('/gs_apprev', methods=['GET', 'POST'])
def gs_apprev():
  if 'user_type' not in session:
    return redirect ('/not_allowed')
  if session['user_type'] != 'grad_sec':
    return redirect ('/not_allowed')
  connection = mydb.cursor(dictionary=True, buffered = True)
  connection.execute("SELECT count(*) FROM applications")
  count = connection.fetchall()
  num = count[0].get("count(*)")
  if num == 0:
    return render_template("gs_apprev.html", message = "There are currently no applicants!")

  connection.execute("SELECT * FROM applications JOIN users ON applications.app_id=users.user_id ")
  applicants = connection.fetchall()

  # for applicant in applicants:
  #   print("gs_apprev --- app: " + str(applicant['app_id']) + " app stat: " + str(applicant['app_stat']))

  
  return render_template("gs_apprev.html", applicants = applicants )


  #----------------------------------------------------------------------------------------------
  #REGS
  #----------------------------------------------------------------------------------------------
  
@app.route('/regs', methods=['GET', 'POST'])
def regs_home():
  login = False
  if 'uname' in session:
      login = True
  return render_template('home.html', login=login)


grades = {
    "A": 4.0,
    "A-": 3.7,
    "B+": 3.3,
    "B": 3.0,
    "B-": 2.7,
    "C+": 2.3,
    "C": 2.0,
    "C-": 1.7,
    "D+": 1.3,
    "D": 1.0,
    "D-": 0.7,
    "F": 0.0
}

# CUR_SEM = "Spring"
# CUR_YEAR = "2022"


@app.route('/regs_transcript/<user_id>')
def regs_transcript(user_id):
  print(user_id)
  print(session['user_id'])
  if 'user_type' not in session:
    return redirect ('/not_allowed')
  if int(session['user_id']) == int(user_id) or session['user_type'] == 'fac_adv' or session['user_type'] == 'alumni':
    # set up cursor and DB connection
    cursor = mydb.cursor(dictionary=True, buffered=True)
    # get courses a student has taken, ordered by year/semester
    cursor.execute("SELECT * FROM enrolled_in JOIN courses ON courses.course_id = enrolled_in.course_id HAVING student_id = %s ORDER BY year, semester", (user_id, ))
    courses = cursor.fetchall()
    # get all semesters that a student has taken courses
    cursor.execute("SELECT DISTINCT semester, year FROM enrolled_in WHERE student_id = %s", (user_id,))
    sems = cursor.fetchall()

    cursor.execute("SELECT fname, lname FROM users WHERE user_id =%s", (user_id,))
    name = cursor.fetchone()
    name = name['fname'] + ' ' + name['lname']

    # get each semester's gpa
    # these will have matching keys

    # courses in the semester
    semester = dict()
    # gpa for each semester
    sem_gpas = dict()
    for sem in sems:
        # create key of the form SEM YEAR ex. FALL 2022
        key = sem['semester'] + " " + sem['year']
        cursor.execute("SELECT * FROM enrolled_in JOIN courses ON courses.course_id = enrolled_in.course_id HAVING student_id = %s AND year = %s AND semester = %s",
                      (user_id, sem['year'], sem['semester']))
        c_sem = cursor.fetchall()

        # courses in the semester
        semester[key] = c_sem
        s_gpa = 0.0
        for c in c_sem:
            if grades.get(c['grade']):
                s_gpa += grades.get(c['grade'])
        if len(c_sem) != 0:
            s_gpa /= len(c_sem)
            s_gpa = "{:.2f}".format(s_gpa)
        # gpa of the semester
        sem_gpas[key] = s_gpa
    # calculate cumulative GPA and credits earned
    cum_gpa = 0.0
    hours = 0
    total = 0
    for course in courses:
        # only add if there is a grade in the dict -- cannot earn credit for IP, W, etc
        if(grades.get(course['grade'])):
            total += 1
            hours += course['credits']
            cum_gpa += grades.get(course['grade'])
    if total != 0:
        cum_gpa /= total
        cum_gpa = "{:.2f}".format(cum_gpa)
    if session['user_type'] == 'alumni':
      cursor.execute("SELECT * FROM alumni")
      alumni_info = cursor.fetchone()
      program = alumni_info['program']
      year = alumni_info['grad_yr']
      return render_template("regs_transcript.html", semesters=semester, gpas=sem_gpas, cum_gpa=cum_gpa, credits=hours, name = name, program = program, year = year)
    return render_template("regs_transcript.html", semesters=semester, gpas=sem_gpas, cum_gpa=cum_gpa, credits=hours, name = name)
  else:
    return redirect('/not_allowed')

@app.route('/regs_register')
def regs_register():
    # This makes the assumption that the courses in 'courses_offered'
    # are for the semester a student can currently register for.

    # set up cursor/DB connection
    if 'user_type' not in session:
      return redirect ('/not_allowed')
    if session['user_type'] != 'student':
      return redirect('/not_allowed')
    cursor = mydb.cursor(dictionary=True, buffered=True)
    cursor.execute(
        "SELECT * FROM courses_offered JOIN courses ON courses.course_id = courses_offered.course_id")
    courses = cursor.fetchall()
    # show courses that are being offered
    return render_template("regs_register.html", courses=courses)

@app.route('/regs_register/<title>', methods=['GET', 'POST'])
def regs_registercid(title):
  # this method adds a given course to a student's "cart", stored in a session variable.
  # these courses are only added to their enrollment once they click "Complete Registration"
  if 'name' not in session:
      return render_template("regs_register.html", err=1)
  if request.method == "POST":
      # you can add any course to your cart, validation (overlappting times, proper prerequsities)
      # is once "complete registration" is clicked
      if 'oldcart' not in session:
          session['oldcart'] = list()
          cart = [title]
          session['oldcart'] = cart
      else:
          cart = session['oldcart']
          cart.append(title)
          session['oldcart'] = cart
  return redirect('/regs_register')

@app.route('/regs_remove/<title>', methods=['GET', 'POST'])
def regs_removecid(title):
  # this method removes a course from the "cart"
  # you can only remove a course once it is in your cart, this is based in the HTML
  if 'name' not in session:
      return render_template("regs_register.html", err=1)
  if request.method == "POST":
      if 'oldcart' in session:
          cart = session['oldcart']
          cart.remove(title)
          session['oldcart'] = cart
  return redirect('/regs_register')

@app.route('/regs_drop/<cid>', methods=['GET', 'POST'])
def regs_dropcid(cid):
  # this method drops a course once it has been registered for
  # accessible via the enrollment page
  if 'name' not in session:
      return render_template("regs_register.html", err=1)
  if request.method == "POST":
      cursor = mydb.cursor(dictionary=True)
      cursor.execute(
          "DELETE FROM enrolled_in WHERE course_id = %s AND student_id = %s", (cid, session['user_id']))
      mydb.commit()

  return redirect('/regs_enrollment')

@app.route('/regs_submit')
def regs_submit():
  # this method is called when the student clicks on "complete registration"
  # checks for validity, and if all courses can be registered for, enrolls a student in the
  # courses they have selected for their cart
  cursor = mydb.cursor(dictionary=True, buffered=True)
  cursor.execute("SELECT * FROM courses_offered JOIN courses ON courses.course_id = courses_offered.course_id")
  courses = cursor.fetchall()
  if 'oldcart' not in session:
      return render_template("regs_register.html", courses=courses, err=4)
  else:
      session['cart'] = list()
      nc = list()
      for c in session['oldcart']:
        cursor.execute("SELECT course_id FROM courses WHERE courses.title LIKE %s", (c,))
        new_course = cursor.fetchone()['course_id']
        nc.append(new_course)
        session['cart'] = nc
      cart = list()
      for course in session['cart']:
          cursor.execute("SELECT * FROM courses_offered JOIN courses ON courses.course_id = courses_offered.course_id HAVING courses.course_id = %s", (course,))
          cart.append(cursor.fetchone())
      # check for the same time slot
      # fix logic here
      for item in cart:
          for other_item in cart:
              if item['course_id'] != other_item['course_id'] and item['day'] == other_item['day']:
                  if (item['end_time'] >= other_item['start_time'] and item['end_time'] <= other_item['end_time']) or (item['start_time'] <= other_item['end_time'] and item['end_time'] >= other_item['end_time']):
                      session.pop('cart')
                      return render_template("regs_register.html", courses=courses, err=3)

      cursor.execute("SELECT * FROM enrolled_in JOIN courses_offered ON enrolled_in.course_id = courses_offered.course_id WHERE student_id = %s AND grade = 'IP'", (session['user_id'],))
      in_progress = cursor.fetchall()
      for item in cart:
          for other_item in in_progress:
              if item['course_id'] != other_item['course_id'] and item['day'] == other_item['day']:
                  if (item['end_time'] >= other_item['start_time'] and item['end_time'] <= other_item['end_time']) or (item['start_time'] <= other_item['end_time'] and item['end_time'] >= other_item['end_time']):
                      session.pop('cart')
                      return render_template("regs_register.html", courses=courses, err=3)

      # another error check: make sure they haven't already taken the course!!

      cursor.execute("SELECT * FROM enrolled_in WHERE student_id = %s", (session['user_id'],))
      taken = cursor.fetchall()
      for item in cart:
          for other_item in taken:
              if item['course_id'] == other_item['course_id']:
                  session.pop('cart')
                  return render_template("regs_register.html", courses=courses, err=5)

      cursor.execute("SELECT * FROM constants")
      constants = cursor.fetchone()
      # print(constants)
      for course in session['cart']:
          # ensure prerequisites have already been taken
          cursor.execute("SELECT * FROM prereq_of WHERE course_id LIKE %s", (course,))
          prereqs = cursor.fetchall()
          cursor.execute("SELECT * FROM enrolled_in WHERE student_id LIKE %s", (session['user_id'],))
          taken = cursor.fetchall()
          taken_list = list()
          for t in taken:
              taken_list.append(t['course_id'])
          for pr in prereqs:
              if pr['pr_cid'] not in taken_list:
                  session.pop('cart')
                  cursor.execute("SELECT * FROM courses_offered JOIN courses ON courses.course_id = courses_offered.course_id")
                  courses = cursor.fetchall()
                  return render_template("regs_register.html", courses=courses, err=2, pr=pr)

          cursor.execute("INSERT INTO enrolled_in VALUES (%s, %s, %s, %s, %s)", (session['user_id'], course, constants['cur_sem'], constants['cur_year'], 'IP'))
          mydb.commit()
      cursor.close()
      session.pop('cart')
  return redirect('/home')

@app.route('/regs_grade_entry', methods=['GET', 'POST'])
def regs_grade_entry():
  if 'user_type' not in session:
    return redirect ('/not_allowed')
  if session['user_type'] == 'grad_sec' or  session['user_type'] == 'Instructor':
    cursor = mydb.cursor(dictionary=True, buffered=True)
    if session['user_type'] == 'Instructor':
        cursor.execute("SELECT courses.title FROM teaches INNER JOIN courses ON teaches.course_id = courses.course_id WHERE teaches.faculty_id = %s AND teaches.semester = 'Spring' AND teaches.year = '2022'", (session['user_id'],))
        coursesteachingfetch = cursor.fetchall()
        coursesteaching = list()
        for course in coursesteachingfetch:
            coursesteaching.append(course['title'])
    elif session['user_type'] == 'grad_sec':
        cursor.execute("SELECT courses.title FROM courses INNER JOIN courses_offered ON courses.course_id = courses_offered.course_id")
        coursesteachingfetch = cursor.fetchall()
        coursesteaching = list()
        for course in coursesteachingfetch:
            coursesteaching.append(course['title'])
    courseselected = request.args.get('class')
    cursor.execute("SELECT users.* FROM users INNER JOIN enrolled_in ON users.user_id = enrolled_in.student_id INNER JOIN courses ON enrolled_in.course_id = courses.course_id WHERE courses.title = %s", (courseselected,))
    studentsfetch = cursor.fetchall()
    students = list()
    for student in studentsfetch:
        if session['user_type'] == 'Instructor':
            cursor.execute("SELECT enrolled_in.grade FROM enrolled_in INNER JOIN courses ON enrolled_in.course_id = courses.course_id WHERE enrolled_in.student_id = %s AND courses.title = %s",(student['user_id'], courseselected))
            gradefetch = cursor.fetchone()['grade']
            if gradefetch == 'IP':
                studentdict = {'student_id': student['user_id'], 'fname': student['fname'], 'lname': student['lname'], 'currentgrade': "IP"}
                students.append(studentdict)
        elif session['user_type'] == 'grad_sec':
            cursor.execute("SELECT enrolled_in.grade FROM enrolled_in INNER JOIN courses ON enrolled_in.course_id = courses.course_id WHERE enrolled_in.student_id = %s AND courses.title = %s",(student['user_id'], courseselected))
            gradefetch = cursor.fetchone()['grade']
            studentdict = {'student_id': student['user_id'], 'fname': student['fname'], 'lname': student['lname'], 'currentgrade': gradefetch}
            students.append(studentdict)
    studentselected = request.args.get('student')
    gradeselected = request.args.get('grade')
    if courseselected != None and studentselected != None and gradeselected != None:
      # print("Course: " + courseselected + " Student: " + studentselected + " Grade: " + gradeselected)
      allinfo = request.args.to_dict(flat=False)
      # print(allinfo)
      for i in range(len(allinfo['student'])):
        # print(i)
        # print(len(allinfo['student']))
        cur_student = allinfo['student'][i]
        cur_grade = allinfo['grade'][i]
        # print(cur_student)
        # print(cur_grade)
        cursor.execute("UPDATE enrolled_in INNER JOIN courses ON enrolled_in.course_id = courses.course_id SET enrolled_in.grade = %s WHERE enrolled_in.student_id = %s AND courses.title = %s",(cur_grade, cur_student, courseselected))
        mydb.commit()
      return redirect(request.referrer)
    return render_template("regs_grade_entry.html", courses=coursesteaching, courseselected=courseselected, students=students, studentselected=studentselected, grades=grades, gradeselected=gradeselected)
  else:
    return redirect ('/not_allowed')

@app.route('/regs_enrollment')
def regs_enrollment():
  if 'user_type' not in session:
    return redirect ('/not_allowed')
  if session['user_type'] != 'student':
    return redirect('/not_allowed')
  # shows courses that a student is currently enrolled in
  cursor = mydb.cursor(dictionary=True, buffered=True)
  cursor.execute("SELECT * FROM constants")
  constants = cursor.fetchone()
  cursor.execute("SELECT course_id FROM enrolled_in WHERE student_id LIKE %s AND semester LIKE %s AND year LIKE %s",(session['user_id'], constants['cur_sem'], constants['cur_year']))
  courses = cursor.fetchall()
  enrollment = list()
  for course in courses:
      cursor.execute("SELECT * FROM courses JOIN enrolled_in ON courses.course_id = enrolled_in.course_id HAVING courses.course_id LIKE %s AND student_id LIKE %s", (course['course_id'], session['user_id']))
      enrollment.append(cursor.fetchone())
  cursor.close()
  return render_template("regs_enrollment.html", year=constants['cur_year'], semester=constants['cur_sem'], courses=enrollment)

@app.route('/regs_coursecatalog')
def regs_coursecatalog():
  if 'user_type' not in session:
    return redirect ('/not_allowed')
  if session['user_type'] != 'student':
    return redirect('/not_allowed')
  cursor = mydb.cursor(dictionary=True, buffered=True)
  cursor.execute("SELECT * FROM courses_offered JOIN courses ON courses.course_id = courses_offered.course_id")
  courses = cursor.fetchall()
  cursor.execute("SELECT * FROM courses")
  allcourses = cursor.fetchall()
  cursor.execute("SELECT * FROM courses JOIN prereq_of ON courses.course_id = prereq_of.pr_cid WHERE courses.course_id")
  c_prereqs = cursor.fetchall()
  cursor.execute("SELECT * FROM prereq_of")
  prereqids = cursor.fetchall()
  prereqs = list()
  for c_prereq in c_prereqs:
      cursor.execute("SELECT * FROM courses HAVING course_id LIKE %s", (c_prereq['pr_cid'],))
      prereqs.append(cursor.fetchone())
  return render_template("regs_catalog.html", courses=courses, c_prereqs=c_prereqs, prereqids=prereqids, prereqs=prereqs, allcourses=allcourses)

@app.route('/chyear')
def chyear():
  cursor = mydb.cursor(dictionary=True, buffered=True)
  cursor.execute("SELECT * FROM constants")
  yearsem = cursor.fetchone()
  cur_year = yearsem['cur_year']
  cur_sem = yearsem['cur_sem']
  return render_template("regs_administrate.html", cur_year = cur_year, cur_sem = cur_sem)

@app.route('/setsem', methods=['GET', 'POST'])
def setsem():
  if request.method == "POST":
      year = request.form['year']
      sem = request.form['sem']
      # print(year)
      # print(sem)
      cursor = mydb.cursor(dictionary=True, buffered=True)
      cursor.execute("SELECT * FROM constants")
      cur = cursor.fetchone()
      # print(cur)
      cursor.execute("UPDATE constants SET cur_year = %s, cur_sem = %s WHERE cur_year = %s", (year, sem, cur['cur_year']))
      mydb.commit()
      cursor.execute("SELECT * FROM constants")
      cur = cursor.fetchone()
      cur_year = cur['cur_year']
      cur_sem = cur['cur_sem']
      # print(cur_sem)
      # print(cur_year)
      return render_template("regs_administrate.html", cur_year = cur_year, cur_sem=cur_sem, success=1)

@app.route('/accept')
def accept():
  connection = mydb.cursor(dictionary=True, buffered=True)
  connection.execute("UPDATE users SET utype=%s WHERE user_id=%s", ("student", session['user_id']))
  # mydb.commit()
  connection.execute("SELECT deg_sought FROM applications WHERE app_id=%s", (session['user_id'],))
  program=connection.fetchone()
  connection.execute("INSERT INTO students (s_id, program) VALUES (%s, %s)", (session['user_id'], program['deg_sought']))
  # mydb.commit()
  connection.execute("DELETE FROM applications WHERE app_id=%s", (session['user_id'],))
  connection.execute("DELETE FROM degrees WHERE app_id=%s", (session['user_id'],))
  connection.execute("DELETE FROM tests WHERE app_id=%s", (session['user_id'],))
  mydb.commit()
  session['user_type'] = "student"
  return redirect('/home')

@app.route('/reject')
def reject():
  connection = mydb.cursor(dictionary=True, buffered=True)
  connection.execute("DELETE FROM degrees WHERE app_id=%s", (session['user_id'],))
  connection.execute("DELETE FROM applications WHERE app_id=%s", (session['user_id'],))
  connection.execute("DELETE FROM tests WHERE app_id=%s", (session['user_id'],))
  connection.execute("DELETE FROM users WHERE user_id=%s", (session['user_id'],))
  mydb.commit()
  return redirect('/logout')

@app.route('/new-stud/<sid>', methods=['GET', 'POST'])
def newstud(sid):
  if request.method == 'POST':
    prog=request.form['field_prog']
    connection = mydb.cursor(dictionary=True, buffered=True)
    connection.execute("INSERT INTO students (s_id, program) VALUES (%s, %s)",(sid, prog))
    mydb.commit()
    return redirect('/home')

  return render_template("new_stud.html", uid=sid)

@app.route('/delete_user/<uid>')
def delete_user(uid):
  cursor = mydb.cursor(dictionary=True, buffered=True)
  cursor.execute("SELECT utype FROM users WHERE user_id=%s", (int(uid), ))
  utype = cursor.fetchone()
  if utype['utype'] == 'student':
    cursor.execute("DELETE FROM advises WHERE s_id=%s", (int(uid), ))
    cursor.execute("DELETE FROM applies WHERE s_id=%s", (int(uid), ))
    cursor.execute("SELECT * FROM form_one WHERE s_id=%s", (int(uid), ))
    form_one = cursor.fetchall()
    for item in form_one:
      cursor.execute("DELETE FROM form_one WHERE s_id=%s", (int(uid), ))
    cursor.execute("DELETE FROM students WHERE s_id=%s", (int(uid), ))
  if utype['utype'] == 'alumni':
    cursor.execute("DELETE FROM alumni WHERE alumni_id=%s", (int(uid), ))
  if utype['utype'] == 'fac_adv':
    cursor.execute("DELETE FROM advises WHERE adv_id=%s", (int(uid), ))
  if utype['utype'] == 'applicant':
    cursor.execute("DELETE FROM applications WHERE app_id=%s", (int(uid), ))
    cursor.execute("DELETE FROM tests WHERE app_id=%s", (int(uid), ))
    cursor.execute("DELETE FROM rec_letters WHERE app_id=%s", (int(uid), ))
    cursor.execute("DELETE FROM reviews WHERE app_id=%s", (int(uid), ))
    cursor.execute("DELETE FROM degrees WHERE app_id=%s", (int(uid), ))
  if utype['utype'] == 'fac_adv':
    cursor.execute("DELETE FROM advises WHERE adv_id=%s", (int(uid), ))
  cursor.execute("DELETE FROM users WHERE user_id=%s", (int(uid), ))
  mydb.commit()

  #need to be able to delete from tables where references
  return redirect('/home')

@app.route('/not_allowed')
def not_allowed():
  return render_template("not_allowed.html")
app.run(host='0.0.0.0', port=8080)