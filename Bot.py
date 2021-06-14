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

SAMPLE_SPREADSHEET_ID = 'xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx'

service = build('sheets', 'v4', credentials=creds)

sheet = service.spreadsheets()
result = sheet.values().get(spreadsheetId=SAMPLE_SPREADSHEET_ID,
                            range="Sheet!A2:A").execute()

values = result.get('values',[])

zip_result = sheet.values().get(spreadsheetId=SAMPLE_SPREADSHEET_ID,
                range="Sheet!C2:C").execute()

zip_values = zip_result.get('values',[])
user_input = [['YES']]
messagenumber = " "
order_list_for_zip = {}
sr_no_list = []


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
        y='xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx'
        msg.body(y)
        responded = True

        

    elif incoming_msg.isnumeric():
        global messagenumber
        global sr_no_list #dictionary hatani hai
        zip_mobile_no_list =[]
        zip_order_no_list = []


        if(len(incoming_msg) == 6 ):
            item = 0        
            sr_no = 1
            order_no_list_dict = sheet.values().get(spreadsheetId=SAMPLE_SPREADSHEET_ID,
                        range = "Sheet!A2:A").execute()
            order_no_list = order_no_list_dict ['values']
            moblie_no_list_dict = sheet.values().get(spreadsheetId=SAMPLE_SPREADSHEET_ID,
                        range = "Sheet!B2:B").execute()
            mobile_no_list = moblie_no_list_dict ['values']


            for item in range(len(values)):
                if(zip_values[item] == [incoming_msg] ):
                    pour = str(sr_no) + ":"  + str(values[item][0].replace("#"," "))
                    messagenumber = messagenumber + pour + "\n"
                    sr_no_list.append(item) 
                    zip_mobile_no_list.append(mobile_no_list[item])
                    zip_order_no_list.append(order_no_list[item])
                    sr_no += 1
                    
            ACCOUNT_SID = 'xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx' 
            AUTH_TOKEN = 'xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx' 

            
            iterator = 0
            for order_mobile_no in zip_mobile_no_list :
                order_mobile_no = '+91' + order_mobile_no[0]
                order_no = zip_order_no_list[iterator][0]
                order_no = order_no.replace("#","")
                client = Client(ACCOUNT_SID, AUTH_TOKEN)
                message = client.messages.create( 
                                    from_='xxxxxxxxxxxx',  
                                    body='Your order number ' + order_no + ' has been delivered',      
                                    to = order_mobile_no
                                ) 
                message = client.messages.create( 
                                        from_='xxxxxxxxxxxx',  
                                        body='Your order number ' + order_no + ' has been delivered',      
                                        to = 'xxxxxxxxxxxxx'
                                    ) 
                print(message.sid)
                iterator += 1


            msg.body(messagenumber)
            messagenumber = ""
            responded = True
            
        elif (int(incoming_msg) < sr_no_list[-1] + 1):
            inda = sr_no_list[int(incoming_msg)-1]+2
            order_moblie_no_dict = sheet.values().get(spreadsheetId=SAMPLE_SPREADSHEET_ID,
                     range = "Sheet!B" + str(inda)).execute()
            order_mobile_no = order_moblie_no_dict ['values'][0][0]
            order_no_dict = sheet.values().get(spreadsheetId=SAMPLE_SPREADSHEET_ID,
                     range = "Sheet!A" + str(inda)).execute()
            order_no = order_no_dict ['values'][0][0]
            order_no = order_no.replace("#","")

            curr_st= sheet.values().get(spreadsheetId=SAMPLE_SPREADSHEET_ID,
                range = "Sheet!D" + str(inda)).execute()

            if ('values' in curr_st):
                    y="Order number already delivered: " + order_no
                    msg.body(y)        
            else:
                service.spreadsheets().values().append(spreadsheetId=SAMPLE_SPREADSHEET_ID, 
                        range="Sheet!D"+ str(inda), 
                        valueInputOption="USER_ENTERED", 
                        insertDataOption="OVERWRITE", 
                        body={
                        "values": user_input
                    }).execute()
                y = "Order number delivered: " + order_no
                msg.body(y)


                ACCOUNT_SID = 'xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx' 
                AUTH_TOKEN = 'xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx' 

                order_mobile_no = '+91' + order_mobile_no
                client = Client(ACCOUNT_SID, AUTH_TOKEN)
                message = client.messages.create( 
                                    from_='+xxxxxxxxxxxxxx',  
                                    body='Your order number ' + order_no + ' has been delivered',      
                                    to = order_mobile_no
                                ) 
                message = client.messages.create( 
                                    from_='+xxxxxxxxxxxxxx',  
                                    body='Your order number ' + order_no + ' has been delivered',      
                                    to = '+xxxxxxxxxxxxxx'
                                ) 
                print(message.sid)
            responded = True


        else:
            y = "Invalid Order Number"
            msg.body(y)
            responded = True
        
        order_list_for_zip = messagenumber


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
