from flask import Flask, request
from pyasn1_modules.rfc2459 import PrivateDomainName
from twilio.rest import Client
from twilio.twiml.messaging_response import MessagingResponse
import gspread
from googleapiclient.discovery import build
from google.oauth2 import service_account
from werkzeug.utils import find_modules

SERVICE_ACCOUNT_FILE = 'credentials.json'
SCOPES = ['https://www.googleapis.com/auth/spreadsheets']

creds = None
creds = service_account.Credentials.from_service_account_file(
        SERVICE_ACCOUNT_FILE, scopes=SCOPES)

SAMPLE_SPREADSHEET_ID = 'XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX'

service = build('sheets', 'v4', credentials=creds)

sheet = service.spreadsheets()
result = sheet.values().get(spreadsheetId=SAMPLE_SPREADSHEET_ID,
                            range="BillingPhone!A2:A").execute()

values = result.get('values',[])

zip_result = sheet.values().get(spreadsheetId=SAMPLE_SPREADSHEET_ID,
                range="BillingPhone!C2:C").execute()

zip_values = zip_result.get('values',[])
user_input = [['YES']]
messagenumber = " "

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
        y='Hi! We are from FruitBox. \n\nPLEASE ENTER YOUR ZIP CODE !?'
        msg.body(y)
        responded = True

    elif incoming_msg.isnumeric():
        global messagenumber

        if(len(incoming_msg) == 6 ):
            item = 0        
            sr_no = 1
            for item in range(len(values)):
                if(zip_values[item] == [incoming_msg] ):
                    pour = str(sr_no) + ":"  + str(values[item][0].replace("#"," "))
                    messagenumber = messagenumber + pour + "\n"
                    sr_no += 1 
            msg.body(messagenumber)
            responded = True

        elif ["#" + incoming_msg] in values[:]:
            inda = values[:].index(["#" + incoming_msg]) + 2

            curr_st= sheet.values().get(spreadsheetId=SAMPLE_SPREADSHEET_ID,
                range = "BillingPhone!D" + str(inda)).execute()

            if( 'values' in curr_st):
                y="Order number already delivered: " + incoming_msg
                msg.body(y)        
            else:
                service.spreadsheets().values().append(spreadsheetId=SAMPLE_SPREADSHEET_ID, 
                        range="BillingPhone!D"+ str(inda), 
                        valueInputOption="USER_ENTERED", 
                        insertDataOption="OVERWRITE", 
                        body={
                        "values": user_input
                    }).execute()
                y="Order number delivered: " + incoming_msg
                msg.body(y)
             
                ACCOUNT_SID = 'XXXXXXXXXXXXXXXXXXXXXXXX' 
                AUTH_TOKEN = 'XXXXXXXXXXXXXXXXXXXXXXXXX' 

                phone_no_list = sheet.values().get(spreadsheetId=SAMPLE_SPREADSHEET_ID,
                    range = "BillingPhone!B" + str(inda)).execute()
                phone_no = '+91' + phone_no_list.get('values',[])[0][0]

                client = Client(ACCOUNT_SID, AUTH_TOKEN)
                message = client.messages.create( 
                                    from_='XXXXXXXXXXXXXXXX',  
                                    body='Your order number ' + incoming_msg + ' has been delivered',      
                                    to = phone_no
                                ) 
                print(message.sid)
            responded = True

            
        else:
            y = "Invalid Order Number"
            msg.body(y)
            responded = True


    elif 'thanks' in incoming_msg:
        y="Thanks for visiting our store"
        msg.body(y)
        responded = True

    else:
        y = "Invalid input operation."
        msg.body(y)
        responded = True
        
    if not responded:
        y = "invalid response"
        msg.body(y)
    return str(resp)
    

if __name__ == '__main__':
    app.run(debug=True)

