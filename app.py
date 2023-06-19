import anvil.server
import psycopg2 as pg2
#import time

from datetime import date, datetime
import os

uplink_key = os.environ['UPLINK_KEY'] 
anvil.server.connect(uplink_key)

'''
# LOCAL - Remove the following lines for Heroku

'''
# HEROKU - ADD THESE INSTEAD:
DB_HOST = os.environ.get('DB_HOST')
DB_NAME = os.environ.get('DB_NAME')
DB_USER = os.environ.get('DB_USER')
DB_PASSWORD = os.environ.get('DB_PASSWORD')


#Heroku
conn = pg2.connect(
    host=DB_HOST,
    port='5432',
    dbname=DB_NAME,
    user=DB_USER,
    password=DB_PASSWORD,
    sslmode='prefer',
    connect_timeout=10
    )



@anvil.server.callable
def get_emails_names():
  try: 
      cur = conn.cursor()
  
      cur.execute('SELECT * FROM users;')
      emails_names = cur.fetchall()    
  except Exception as e:
      conn.rollback()
      print(e)
  
  return emails_names


@anvil.server.callable
def get_quote_variables(email):
  cur = conn.cursor()
  cur.execute('SELECT * FROM estimate_variables WHERE email = %s;', (email,))
  variables =  cur.fetchall()
  cur.close()
  return variables


@anvil.server.callable
def get_items():
  cur.execute('SELECT * FROM currentSelection WHERE id = 1;')
  items = cur.fetchall()
  
  return items
  

@anvil.server.callable
def say_hello(name):
  response = ("Hello from you Macbook M1 uplink, %s!" % name)
  print('You are in your own Terminal - ',response)
  return response


@anvil.server.callable
def fetchQuoteDicts(quoteID):
  cur = conn.cursor()
  cur.execute('SELECT * FROM estimate_descriptions WHERE estimate_id = %s;', (quoteID,))
  descriptions =  cur.fetchone()

  cur.execute('SELECT * FROM estimate_values WHERE estimate_id = %s;', (quoteID,))
  values = cur.fetchone()


  # Create Dict from descriptions[4] while descriptions[n]!=None & values[4] while...
  list_of_Description_Amount = []

  for desc, value in zip(descriptions[4:], values[4:]):
    if desc == None or value == None:
        break
        
    list_of_Description_Amount.append({'Description': desc,  
                                       'Amount': '£'+str(value)})

  # Get total from values[3]
  list_of_Description_Amount.append({'Description': descriptions[3], 'Amount': '£'+str(values[3])})

  cur.close()

  return list_of_Description_Amount


@anvil.server.callable
def fetchActivityList():

  cur = conn.cursor()
  cur.execute('SELECT email, created_at FROM estimate_variables;')
  activity =  cur.fetchall()

  activityList = []
  for act in activity:
    email = act[0].lower()
    date = act[1].strftime("%Y-%m-%d") 
    time = act[1].strftime("%H:%M:%S")
    activityList.append(f'{date} {time} - {email}')

  return activityList



@anvil.server.callable
def fetchActivityDates():

  def remove_duplicates(lst):
    return list({value: None for value in lst}.keys())

  def sortActivityLists(activity):
    # Create lists from raw data
    actions, emails, dates = [],[],[]
    for action in activity:
      dates.append(action[1].date())
      actions.append([action[0].lower(), action[1].date()])

    return dates, actions


  def Date_list_of_strings(dates, reversed):

    dates_strList = []
    dates_NoDuplicates = remove_duplicates(dates)
    dates_NoDuplicates.sort(reverse=reversed)
    for date in dates_NoDuplicates:
      dates_strList.append(date.strftime("%d/%m/%y"))

    return dates_strList

  def nested_QuotesPerDay(sorted_actions):
    
    #start on first day
    date = sorted_actions[0][1] #start on first day
    totalCount = actionCount = 0
    daily_emails, email_per_day = [], []
    actions_per_day = []
    n=0

    for day in sorted_actions:
      
      if date == day[1]:
        n+=1
        actionCount += 1
        totalCount += 1
        if day[0] not in daily_emails:
          daily_emails.append(day[0])

      else:
        n=0
        actions_per_day.append([date,actionCount])
        email_per_day.append([date,len(daily_emails)])
        date = day[1]
        actionCount = 0
        daily_emails.clear()


    return actions_per_day, email_per_day


  cur = conn.cursor()
  cur.execute('SELECT email, created_at FROM estimate_variables;')
  activity =  cur.fetchall()

  dates, actions = sortActivityLists(activity)

  reversed_dates = Date_list_of_strings(dates, True)

  sorted_dates = Date_list_of_strings(dates, False)

  sorted_actions = sorted(actions, key=lambda x: x[1])

  # Make a nested List with quotes per day
  dailyActions, dailyUsers = nested_QuotesPerDay(sorted_actions)


  return sorted_dates, reversed_dates, dailyActions, dailyUsers




def CreateListsForPieChart(schema):

  Names, Count = [],[]
  sch_counter = 0
  quote_counter = 0

  cur = conn.cursor()
  # Execute the SQL query to retrieve the rows where chip_iot is not NULL and equal to 1
  cur.execute("SELECT * FROM estimate_variables")
  est_vars = cur.fetchall()

  quote_counter = cur.rowcount

  for sch in schema:
      
      for row in est_vars:
        
        # element starts at 0 not 1 so sf[1]-1
        if row[sch[1]-1] == 1:
          sch_counter += 1
      Names.append(sch[0])
      Count.append(sch_counter)
      
      sch_counter = 0

  # Calculate the % of each selection by the amount of quotes

  Percent = [num/quote_counter for num in Count] if quote_counter != 0 else [0 for num in Count]

  return Names, Count, Percent, quote_counter



@anvil.server.callable
def fetchFeatureList():

  # Create a list of the db using features Name and column Position
  schemaFeatures = [['Dashboard',13],['Staff Management',14],['Customer Management',15],
  ['Activity Flow',16],['Ratings/Reviews',17],['Animations',18],
  ['Analytics',19],['QR Codes',20],['Calculator/Tools',21],
  ['Video Streaming',22],['File Upload',21],['Calendar',24],
  ['Other Features',25]]

  featureNames, featureCount, featurePercent, quote_counter = CreateListsForPieChart(schemaFeatures)
  
  return featureNames, featureCount, featurePercent, quote_counter


@anvil.server.callable
def fetchIntergrationList():
  
  # Create a list of the db using intergration Name and column Position
  schemaIntergrations = [['Staff Management',14], ['Payments', 26],
   ['Email',27], ['Maps', 28], ['IoT',29,'chip_iot'], 
   ['SMS',30], ['Finance',31],['Delivery',32], 
   ['Chat',33],['CRM',14], ['ERP',10], 
   ['Fitness',12], ['Other Intergrations',9]]


  intergrNames, intergrCount, intergrPercent, quote_counter = CreateListsForPieChart(schemaIntergrations)
  
  return intergrNames, intergrCount, intergrPercent, quote_counter


@anvil.server.callable
def fetchSelectionList():

  cur = conn.cursor()
  # Execute the SQL query to retrieve the rows where chip_iot is not NULL and equal to 1
  cur.execute("SELECT * FROM estimate_variables")
  est_vars = cur.fetchall()

  businessList, webList, qualityList, authList  = [], [], [], []
  businessCount, webCount, qualityCount, authCount  = [0,0,0], [0,0,0], [0,0,0], [0,0,0]
  for ent in est_vars:

    if ent[2].split('_')[1] not in businessList:
      businessList.append(ent[2].split('_')[1])  # Add the human name for the variable
    i = businessList.index(ent[2].split('_')[1])
    businessCount[i]+=1

    if ent[3].split('_')[1] not in webList:
      webList.append(ent[3].split('_')[1])  # Add the human name for the variable
    i = webList.index(ent[3].split('_')[1])
    webCount[i]+=1

    if ent[4].split('_')[1] not in qualityList:
      qualityList.append(ent[4].split('_')[1])  # Add the human name for the variable
    i = qualityList.index(ent[4].split('_')[1])
    qualityCount[i]+=1

    if ent[5].split('_')[1] not in authList:
      authList.append(ent[5].split('_')[1])  # Add the human name for the variable
    i = authList.index(ent[5].split('_')[1])
    authCount[i]+=1

  return businessList,businessCount,webList,webCount,qualityList,qualityCount,authList,authCount



# Start the Anvil server
anvil.server.wait_forever()
















