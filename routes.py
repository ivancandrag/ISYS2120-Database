# Importing the Flask Framework

from modules import *
from flask import *
import database
import configparser


# appsetup

page = {}
session = {}

# Initialise the FLASK application
app = Flask(__name__)
app.secret_key = 'SoMeSeCrEtKeYhErE'


# Debug = true if you want debug output on error ; change to false if you dont
app.debug = True


# Read my unikey to show me a personalised app
config = configparser.ConfigParser()
config.read('config.ini')
dbuser = config['DATABASE']['user']
portchoice = config['FLASK']['port']
if portchoice == '5xxx':
    print('ERROR: Please change config.ini as in the comments or Lab 08 instructions')
    exit(0)
session['isadmin'] = False

###########################################################################################
###########################################################################################
####                                 Database operative routes                         ####
###########################################################################################
###########################################################################################



#####################################################
##  INDEX
#####################################################

# What happens when we go to our website
@app.route('/')
def index():
    # If the user is not logged in, then make them go to the login page
    if( 'logged_in' not in session or not session['logged_in']):
        return redirect(url_for('login'))
    page['username'] = dbuser
    page['title'] = 'Welcome'
    return render_template('welcome.html', session=session, page=page)

#####################################################
# User Login related                        
#####################################################
# login
@app.route('/login', methods=['POST', 'GET'])
def login():
    page = {'title' : 'Login', 'dbuser' : dbuser}
    # If it's a post method handle it nicely
    if(request.method == 'POST'):
        # Get our login value
        val = database.check_login(request.form['userid'], request.form['password'])
        print(val)
        print(request.form)
        # If our database connection gave back an error
        if(val == None):
            errortext = "Error with the database connection."
            errortext += "Please check your terminal and make sure you updated your INI files."
            flash(errortext)
            return redirect(url_for('login'))

        # If it's null, or nothing came up, flash a message saying error
        # And make them go back to the login screen
        if(val is None or len(val) < 1):
            flash('There was an error logging you in')
            return redirect(url_for('login'))
        # If it was successful, then we can log them in :)
        print(val[0])
        session['name'] = val[0]['firstname']
        session['userid'] = request.form['userid']
        session['logged_in'] = True
        session['isadmin'] = val[0]['isadmin']
        return redirect(url_for('index'))
    else:
        # Else, they're just looking at the page :)
        if('logged_in' in session and session['logged_in'] == True):
            return redirect(url_for('index'))
        return render_template('index.html', page=page)

# logout
@app.route('/logout')
def logout():
    session['logged_in'] = False
    flash('You have been logged out')
    return redirect(url_for('index'))



########################
#List All Items#
########################

@app.route('/users')
def list_users():
    '''
    List all rows in users by calling the relvant database calls and pushing to the appropriate template
    '''
    # connect to the database and call the relevant function
    users_listdict = database.list_users()

    # Handle the null condition
    if (users_listdict is None):
        # Create an empty list and show error message
        users_listdict = []
        flash('Error, there are no rows in users')
    page['title'] = 'List Contents of users'
    return render_template('list_users.html', page=page, session=session, users=users_listdict)
    

########################
#List Single Items#
########################


@app.route('/users/<userid>')
def list_single_users(userid):
    '''
    List all rows in users that match a particular id attribute userid by calling the 
    relevant database calls and pushing to the appropriate template
    '''

    # connect to the database and call the relevant function
    users_listdict = None
    users_listdict = database.list_users_equifilter("userid", userid)

    # Handle the null condition
    if (users_listdict is None or len(users_listdict) == 0):
        # Create an empty list and show error message
        users_listdict = []
        flash('Error, there are no rows in users that match the attribute "userid" for the value '+userid)
    page['title'] = 'List Single userid for users'
    return render_template('list_users.html', page=page, session=session, users=users_listdict)


########################
#List Search Items#
########################

@app.route('/consolidated/users')
def list_consolidated_users():
    '''
    List all rows in users join userroles 
    by calling the relvant database calls and pushing to the appropriate template
    '''
    # connect to the database and call the relevant function
    users_userroles_listdict = database.list_consolidated_users()

    # Handle the null condition
    if (users_userroles_listdict is None):
        # Create an empty list and show error message
        users_userroles_listdict = []
        flash('Error, there are no rows in users_userroles_listdict')
    page['title'] = 'List Contents of Users join Userroles'
    return render_template('list_consolidated_users.html', page=page, session=session, users=users_userroles_listdict)

@app.route('/user_stats')
def list_user_stats():
    '''
    List some user stats
    '''
    # connect to the database and call the relevant function
    user_stats = database.list_user_stats()

    # Handle the null condition
    if (user_stats is None):
        # Create an empty list and show error message
        user_stats = []
        flash('Error, there are no rows in user_stats')
    page['title'] = 'User Stats'
    return render_template('list_user_stats.html', page=page, session=session, users=user_stats)

@app.route('/users/search', methods=['POST', 'GET'])
def search_users_byname():
    print('hi')
    '''
    List all rows in users that match a particular name
    by calling the relevant database calls and pushing to the appropriate template
    '''
    if(request.method == 'POST'):

        fnamesearch = database.search_users_customfilter("firstname","~",request.form['searchterm'])
        print(fnamesearch)
        lnamesearch = database.search_users_customfilter("lastname","~",request.form['searchterm'])
        print(lnamesearch)
        
        users_listdict = None

        if((fnamesearch == None) and (lnamesearch == None)):
            errortext = "Error with the database connection."
            errortext += "Please check your terminal and make sure you updated your INI files."
            flash(errortext)
            return redirect(url_for('index'))
        if(((fnamesearch == None) and (lnamesearch == None)) or ((len(fnamesearch) < 1) and len(lnamesearch) < 1)):
            flash(f"No items found for searchterm: {request.form['searchterm']}")
            return redirect(url_for('index'))
        else:
            
            users_listdict = fnamesearch
            users_listdict.extend(lnamesearch)
            # Handle the null condition'
            print(users_listdict)
            if (users_listdict is None or len(users_listdict) == 0):
                # Create an empty list and show error ssage
                users_listdict = []
                flash('Error, there are no rows in users that match the searchterm '+request.form['searchterm'])
            page['title'] = 'Search for a User by name'
            print(users_listdict)
            return render_template('list_users.html', page=page, session=session, users=users_listdict)
            

    else:
        return redirect(url_for('/users'))
        
@app.route('/users/delete/<userid>')
def delete_user(userid):
    '''
    List all rows in stations join stationtypes 
    by calling the relvant database calls and pushing to the appropriate template
    '''
    # connect to the database and call the relevant function
    resultval = database.delete_user(userid)
    
    # users_listdict = database.list_users()

    # # Handle the null condition
    # if (users_listdict is None):
    #     # Create an empty list and show error message
    #     users_listdict = []
    #     flash('Error, there are no rows in stations_stationtypes_listdict')
    page['title'] = f'List users after user {userid} has been deleted'
    return redirect(url_for('list_consolidated_users'))
    
@app.route('/users/update', methods=['POST','GET'])
def update_user():
    """
    Update details for a user
    """
    # # Check if the user is logged in, if not: back to login.
    if('logged_in' not in session or not session['logged_in']):
        return redirect(url_for('login'))
    
    # Need a check for isAdmin

    page['title'] = 'Update user details'

    userslist = None
    print("request form is:")
    newdict = {}
    print(request.form)
    validupdate = False
    # Check your incoming parameters
    if(request.method == 'POST'):

        # verify that the values are available:
        if ('userid' not in request.form):
            # should be an exit condition
            flash("Can not update without a userid")
            return redirect(url_for('list_users'))
        else:
            newdict['userid'] = request.form['userid']
            print("We have a value: ",newdict['userid'])

        if ('firstname' not in request.form):
            newdict['firstname'] = None
        else:
            validupdate = True
            newdict['firstname'] = request.form['firstname']
            print("We have a value: ",newdict['firstname'])

        if ('lastname' not in request.form):
            newdict['lastname'] = None
        else:
            validupdate = True
            newdict['lastname'] = request.form['lastname']
            print("We have a value: ",newdict['lastname'])

        if ('userroleid' not in request.form):
            newdict['userroleid'] = None
        else:
            validupdate = True
            newdict['userroleid'] = request.form['userroleid']
            print("We have a value: ",newdict['userroleid'])

        if ('password' not in request.form):
            newdict['password'] = None
        else:
            validupdate = True
            newdict['password'] = request.form['password']
            print("We have a value: ",newdict['password'])

        print('Update dict is:')
        print(newdict, validupdate)

        if validupdate:
            #forward to the database to manage update
            userslist = database.update_single_user(newdict['userid'],newdict['firstname'],newdict['lastname'],newdict['userroleid'],newdict['password'])
        else:
            # no updates
            flash("No updated values for user with userid")
            return redirect(url_for('list_users'))
        # Should redirect to your newly updated user
        return list_single_users(newdict['userid'])
    else:
        return redirect(url_for('list_consolidated_users'))

@app.route('/users/add', methods=['POST','GET'])
def add_user():
    """
    Add a new User
    """
    # # Check if the user is logged in, if not: back to login.
    if('logged_in' not in session or not session['logged_in']):
        return redirect(url_for('login'))
    
    # Need a check for isAdmin

    page['title'] = 'Add user details'

    userslist = None
    print("request form is:")
    newdict = {}
    print(request.form)

    # Check your incoming parameters
    if(request.method == 'POST'):

        # verify that the values are available:
        
        if ('firstname' not in request.form):
            newdict['firstname'] = 'Empty firstname'
        else:
            newdict['firstname'] = request.form['firstname']
            print("We have a value: ",newdict['firstname'])

        if ('lastname' not in request.form):
            newdict['lastname'] = 'Empty lastname'
        else:
            newdict['lastname'] = request.form['lastname']
            print("We have a value: ",newdict['lastname'])

        if ('userroleid' not in request.form):
            newdict['userroleid'] = 1 # default is traveler
        else:
            newdict['userroleid'] = request.form['userroleid']
            print("We have a value: ",newdict['userroleid'])

        if ('password' not in request.form):
            newdict['password'] = 'blank'
        else:
            newdict['password'] = request.form['password']
            print("We have a value: ",newdict['password'])

        print('Insert parametesrs are:')
        print(newdict)

        database.add_user_insert(newdict['firstname'],newdict['lastname'],newdict['userroleid'],newdict['password'])
        # Should redirect to your newly updated user
        print("did it go wrong here?")
        return redirect(url_for('list_consolidated_users'))
    else:
        # assuming GET request, need to setup for this
        return render_template('add_user.html',
                           session=session,
                           page=page,
                           userroles=database.list_userroles())

#------------------------------------------------------------------------------------------

########################
#List All Items#
########################

@app.route('/trips')
def list_trips():
    '''
    List all rows in trips by calling the relevant database calls and pushing to the appropriate template
    '''
    # connect to the database and call the relevant function
    trips_listdict = database.list_trips()

    # Handle the null condition
    if (trips_listdict is None):
        # Create an empty list and show error message
        trips_listdict = []
        flash('Error, there are no rows in trips')
    page['title'] = 'List Contents of trips'
    return render_template('list_trips.html', page=page, session=session, trips=trips_listdict)
    

########################
#List Single Items#
########################


@app.route('/trips/<tripid>')
def list_single_trips(tripid):
    '''
    List all rows in trips that match a particular id attribute tripid by calling the 
    relevant database calls and pushing to the appropriate template
    '''

    # connect to the database and call the relevant function
    trips_listdict = None
    trips_listdict = database.list_trips_equifilter("tripid", tripid)

    # Handle the null condition
    if (trips_listdict is None or len(trips_listdict) == 0):
        # Create an empty list and show error message
        trips_listdict = []
        flash('Error, there are no rows in trips that match the attribute "tripid" for the value '+tripid)
    page['title'] = 'List Single tripid for trips'
    return render_template('list_trips.html', page=page, session=session, trips=trips_listdict)


########################
#List Search Items#
########################

@app.route('/trip_stats')
def list_trip_stats():
    '''
    List some trip stats
    '''
    # connect to the database and call the relevant function
    trip_stats = database.list_trip_stats()

    # Handle the null condition
    if (trip_stats is None):
        # Create an empty list and show error message
        trip_stats = []
        flash('Error, there are no rows in trip_stats')
    page['title'] = 'trip Stats'
    return render_template('trip_report.html', page=page, session=session, trips=trip_stats)

@app.route('/search', methods=['POST'])
def search_trips_bydate():
    # Filter the dataset based on the input date
    filtered_data = database.search_trips_date("traveldate", request.form['search_date'])

    if not filtered_data:
        flash(f"No items found for search_date: {request.form['search_date']}")
        return redirect(url_for('list_trips'))

    return render_template('list_trips.html', page=page, session=session, trips=filtered_data)
        
@app.route('/trips/delete/<tripid>')
def delete_trip(tripid):
    '''
    List all rows in stations join stationtypes 
    by calling the relvant database calls and pushing to the appropriate template
    '''
    # connect to the database and call the relevant function
    resultval = database.delete_trip(tripid)
    
    # trips_listdict = database.list_trips()

    # # Handle the null condition
    # if (trips_listdict is None):
    #     # Create an empty list and show error message
    #     trips_listdict = []
    #     flash('Error, there are no rows in stations_stationtypes_listdict')
    page['title'] = f'List trips after trip {tripid} has been deleted'
    return redirect(url_for('list_trips'))
    
@app.route('/trips/update', methods=['POST','GET'])
def update_trip():
    """
    Update details for a trip
    """
    # # Check if the trip is logged in, if not: back to login.
    if('logged_in' not in session or not session['logged_in']):
        return redirect(url_for('login'))
    
    # Need a check for isAdmin

    page['title'] = 'Update trip details'

    tripslist = None
    print("request form is:")
    newdict = {}
    print(request.form)
    validupdate = False
    # Check your incoming parameters
    if(request.method == 'POST'):

        # verify that the values are available:
        if ('tripid' not in request.form):
            # should be an exit condition
            flash("Can not update without a tripid")
            return redirect(url_for('list_trips'))
        else:
            newdict['tripid'] = request.form['tripid']
            print("We have a value: ",newdict['tripid'])

        if ('cardid' not in request.form):
            newdict['cardid'] = None
        else:
            validupdate = True
            newdict['cardid'] = request.form['cardid']
            print("We have a value: ",newdict['cardid'])

        if ('traveldate' not in request.form):
            newdict['traveldate'] = None
        else:
            validupdate = True
            newdict['traveldate'] = request.form['traveldate']
            print("We have a value: ",newdict['traveldate'])

        if ('entrystationid' not in request.form):
            newdict['entrystationid'] = None
        else:
            validupdate = True
            newdict['entrystationid'] = request.form['entrystationid']
            print("We have a value: ",newdict['entrystationid'])

        if ('exitstationid' not in request.form):
            newdict['exitstationid'] = None
        else:
            validupdate = True
            newdict['exitstationid'] = request.form['exitstationid']
            print("We have a value: ",newdict['exitstationid'])

        if ('tripstarttime' not in request.form):
            newdict['tripstarttime'] = None
        else:
            validupdate = True
            newdict['tripstarttime'] = request.form['tripstarttime']
            print("We have a value: ",newdict['tripstarttime'])


        print('Update dict is:')
        print(newdict, validupdate)

        if validupdate:
            #forward to the database to manage update
            tripslist = database.update_single_trip(newdict['tripid'],newdict['cardid'],newdict['traveldate'],newdict['entrystationid'],newdict['exitstationid'],newdict['tripstarttime'])
        else:
            # no updates
            flash("No updated values for trip with tripid")
            return redirect(url_for('list_trips'))
        # Should redirect to your newly updated trip
        return list_single_trips(newdict['tripid'])
    else:
        return redirect(url_for('list_trips'))

######
## add items
######

    
@app.route('/trips/add', methods=['POST','GET'])
def add_trip():
    """
    Add a new trip
    """
    # # Check if the trip is logged in, if not: back to login.
    if('logged_in' not in session or not session['logged_in']):
        return redirect(url_for('login'))
    
    # Need a check for isAdmin

    page['title'] = 'Add trip details'

    tripslist = None
    print("request form is:")
    newdict = {}
    print(request.form)

    # Check your incoming parameters
    if(request.method == 'POST'):

        # verify that the values are available:
        
        if ('cardid' not in request.form):
            newdict['cardid'] = 'Empty cardid'
        else:
            newdict['cardid'] = request.form['cardid']
            print("We have a value: ",newdict['cardid'])

        if ('traveldate' not in request.form):
            newdict['traveldate'] = 'Empty traveldate'
        else:
            newdict['traveldate'] = request.form['traveldate']
            print("We have a value: ",newdict['traveldate'])

        if ('entrystationid' not in request.form):
            newdict['entrystationid'] = 1 # default is traveler
        else:
            newdict['entrystationid'] = request.form['entrystationid']
            print("We have a value: ",newdict['entrystationid'])

        if ('exitstationid' not in request.form):
            newdict['exitstationid'] = 'blank'
        else:
            newdict['exitstationid'] = request.form['exitstationid']
            print("We have a value: ",newdict['exitstationid'])

        if ('tripstarttime' not in request.form):
            newdict['tripstarttime'] = 'blank'
        else:
            newdict['tripstarttime'] = request.form['tripstarttime']
            print("We have a value: ",newdict['tripstarttime'])

        print('Insert parameters are:')
        print(newdict)

        database.add_trip_insert(newdict['cardid'],newdict['traveldate'],newdict['entrystationid'],newdict['exitstationid'],newdict['tripstarttime'])
        # Should redirect to your newly updated trip
        print("did it go wrong here?")
        return redirect(url_for('list_trips'))
    else:
        # assuming GET request, need to setup for this
        return render_template('add_trip.html',
                           session=session,
                           page=page,
                           stations=database.list_stations(),
                           opalcards=database.list_opalcards())