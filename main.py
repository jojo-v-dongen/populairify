from flask import Flask, render_template, request, redirect, url_for, make_response, session, flash, abort
from threading import Thread
from send_reset_email import Send_Reset_Email
import populairify
from update_ratings import Update_Leaderboard, Get_Leaderboard
import re


app = Flask(__name__)
app.secret_key = ''
@app.route('/', methods=['GET'])
def index():


  print(session)
  songs = Get_Leaderboard()

  session_data = session if 'user_email' in session else {}
  print(session_data)



  
  return render_template('home_ano.html', songs=songs, session=session_data)
  #return render_template('home_ano.html', songs=songs)
  #return render_template('home_ano.html')


@app.route('/voted/<number_voted>/<song_id>')
def voted(number_voted, song_id):

  # return f'You voted {number_voted}'

  user_email = session['user_email']
  if user_email:
    current_user_email = user_email
  else:
    return redirect(url_for('login_page'))

  def combine_methods(current_user_email, song_id, number_voted):
    populairify.Add_Voted_Song_To_User(current_user_email, song_id)
    populairify.add_vote_to_song(song_id, number_voted)

  # Thread(target=combine_methods, args=(current_user_email, song_id, number_voted)).start()    
  # populairify.Connect_to_DB()
  check = populairify.Check_If_User_Already_Voted(user_email=user_email, song_id=song_id)
  if check == False:
    Thread(target=combine_methods, args=(current_user_email, song_id, number_voted)).start()
    Thread(target=Update_Leaderboard).start()
  else:
     pass

  return redirect(url_for('voting_page'))



@app.route('/voting', methods=['GET', 'POST'])
def voting_page():
  if 'user_email' in session:
    suggestion_message = None

    if request.method == 'POST':
      spotify_url_or_ID = request.form['spotify_url_or_ID']
      user_email = session['user_email']
      pattern = r'track\/([a-zA-Z0-9]+)\?'

      # Check if the user input is a share link or just a song ID
      match = re.search(pattern, spotify_url_or_ID)
      if match:
        spotify_id = match.group(1)
        print("Spotify ID:", spotify_id)

      else:
        spotify_id = spotify_url_or_ID
        print("Spotify ID:", spotify_id)
      
      
      test = populairify.Check_If_Song_Exists(song_id=spotify_id)
      if test:
        suggestion_message = populairify.Add_Song_To_Suggestions(song_id=spotify_id, user_email=user_email)
      else:
        suggestion_message = "Unfortunatelly we could not find the song you submitted."


    user_group = session['user_group']

    Song = populairify.Grab_Song_From_DB(user_group, session['user_email'])
 

    embed = f"https://open.spotify.com/embed/track/{Song}?utm_source=generator"



    return render_template("home_logged.html", song_embed=embed, song_id=Song, suggestion_message=suggestion_message)
  else:
    # User is not logged in
    return redirect(url_for('login_page'))
  

@app.route('/login', methods=['GET', 'POST'])
def login_page():
    
    if 'user_email' in session:
      return redirect(url_for('index'))
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']
        suc_login = populairify.login(email, password)
        if suc_login == True:
            # Store the user's email in a secure session cookie

            username_to_store = populairify.grab_username_from_account(email)
            if username_to_store: username_to_store = username_to_store[0]
            session['user_username'] = username_to_store
            session.permanent = True
            session['user_email'] = email
            session.permanent = True
            session['user_group'] = populairify.grab_user_group_from_account(email=email)
            session.permanent = True
            return redirect(url_for('voting_page'))
        else:
            return render_template('login.html', failed_login_message=suc_login)

 
    return render_template('login.html')


@app.route('/sign-up', methods=['GET', 'POST'])
def signup_page():
  if 'user_email' in session:
    return redirect(url_for('voting_page'))

  if request.method == "POST":
        email = request.form["email"]
        username = request.form["username"]
        password = request.form["password"]
        repeat_password = request.form["repeat_password"]
        if password != repeat_password:
          error_message = "Passwords did not match."
          return render_template("signup.html", error_message=error_message)
        else:
          no_error = populairify.sign_up(username, email, password)
          if no_error == True:
            return redirect(url_for('login_page'))
          else:
            print("SIGNUP FAILED")
            return render_template("signup.html", error_failed_login=no_error)

  return render_template("signup.html")

def Increment_User_Group():
   session['user_group'] = int(populairify.grab_user_group_from_account(session['user_email'])) + 1
   print("::::::::::", session['user_group'])


@app.route('/logout')
def logout_page():

  session.pop('user_username', None)
  session.pop('user_email', None)
  session.pop('user_group', None)
  return redirect(url_for('index'))



@app.route('/forgot_passw', methods=['GET', 'POST'])
def forgot_pass_page():
  if 'user_email' in session:
    return redirect(url_for('voting_page'))

  error_message = None

  if request.method == "POST":
    email = request.form["email"]
  
    if populairify.Check_If_Email_Exists(email):
      reset_url = populairify.Generate_Password_Reset_URL(email)
      username = populairify.grab_username_from_account(email)
      Send_Reset_Email(user_email=email, user_username=username, reset_password_url=reset_url)
      message = "We have sent you an email to reset your password."
      flash(email, 'reset_email')
      print("Flashed", email)
      session['email_for_reset'] = email
      session.permanent = True
      flash(message, 'message')
      return redirect(url_for('login_page'))
    else:
       error_message = "This email does not exist in our database."
       return render_template("forgot_password.html", failed_login_message = error_message)

  return render_template("forgot_password.html")


@app.route('/reset_passw/<id>/<random_url>', methods=['GET', 'POST'])
def reset_pass_page(id, random_url):

  try:
    email = session['email_for_reset']
    if str(populairify.Grab_ID_From_User(email)) != str(id):
      abort(404)


  except KeyError:
    abort(404)



  if request.method == "POST":
    user_email = session['email_for_reset']
    print(user_email)
    password1 = request.form["password"]
    password2 = request.form["password2"]
    if password1 != password2:
       return render_template("reset_password.html", failed_login_message = "Passwords do not match!")
    elif user_email == None:
       return render_template("reset_password.html", failed_login_message = "Error: Email address not provided.\nPlease make sure you have clicked the URL in your email to reset your password.")
    
    changed = populairify.Change_User_Password(user_email=user_email, password=password1)
    if changed:
      session.pop('email_for_reset', None)
      flash("Your password has succesfully been changed.", "pass_change")
      return redirect(url_for('login_page'))
    else:
       return render_template("reset_password.html", failed_login_message = "Error: Something went wrong\nPlease try again later.")
  return render_template("reset_password.html", user_email=email)


if __name__ == "__main__":
    app.run(debug=True)
    