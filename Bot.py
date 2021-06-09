from flask import Flask, request
from twilio.twiml.messaging_response import MessagingResponse
import gspread
from googleapiclient.discovery import build
from google.oauth2 import service_account

SERVICE_ACCOUNT_FILE = 'credentials.json'
SCOPES = ['https://www.googleapis.com/auth/spreadsheets']

creds = None
creds = service_account.Credentials.from_service_account_file(
        SERVICE_ACCOUNT_FILE, scopes=SCOPES)

# The ID and range of a sample spreadsheet.
SAMPLE_SPREADSHEET_ID = 'SPREADSHEET_ID'

service = build('sheets', 'v4', credentials=creds)

sheet = service.spreadsheets()
result = sheet.values().get(spreadsheetId=SAMPLE_SPREADSHEET_ID,
                            range="Sheet!A4:A").execute()

values = result.get('values',[])
user_input = [['YES']]

app = Flask(__name__)

@app.route('/bot', methods=['POST'])
def bot():
    incoming_msg = request.values.get('Body', '').lower()
    resp = MessagingResponse()
    msg = resp.message()
    print('resp',resp)
    print(incoming_msg)
    responded = False

    if 'hi' in incoming_msg:
        y='Hi! \nHow can I help you?'
        msg.body(y)
        responded = True

    if 'orders' in incoming_msg:
        item = 0
        for item in range(len(values) - 1):
                y = str(item+1) + ":"  + str(values[item][0].replace("#"," "))       
                msg.body(y)
        responded = True 

    if 'done' in incoming_msg:
        print("Entered this block")
        print(user_input)
        try:
            service.spreadsheets().values().append(spreadsheetId=SAMPLE_SPREADSHEET_ID, 
                range="SHEET!B1:B", 
                valueInputOption="USER_ENTERED", 
                insertDataOption="INSERT_ROWS", 
                body={
                "values": user_input
            }).execute()
        except:
            print("An error occured")

        y="Thank you! Keep up the good work."
        msg.body(y)
        responded = True


    if 'thanks' in incoming_msg:
        y="Thanks for visiting our store"
        msg.body(y)
        responded = True

    if incoming_msg.isnumeric():
        service.spreadsheets().values().append(spreadsheetId=SAMPLE_SPREADSHEET_ID, 
                range="SHEET!A1:A", 
                valueInputOption="USER_ENTERED", 
                insertDataOption="INSERT_ROWS", 
                body={
                "values": [[incoming_msg]]
            }).execute()
        y="Order number delivered: " + incoming_msg
        msg.body(y)
        responded = True
        

    if not responded:
        msg.body(y)
    return str(resp)

if __name__ == '__main__':
    app.run(debug=True)
