from __future__ import print_function

import os.path

from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError


class GoogleSheet:

    def __init__(self, scopes, spreadsheet_id, working_range):
        self.spreadsheet_id = spreadsheet_id
        self.working_range = working_range
        """Shows basic usage of the Sheets API.
        Prints values from a sample spreadsheet.
        """
        creds = None
        # The file token.json stores the user's access and refresh tokens, and is
        # created automatically when the authorization flow completes for the first
        # time.
        print("path: " + os.path.abspath(os.curdir))
        if os.path.exists('token.json'):
            creds = Credentials.from_authorized_user_file('token.json', scopes)

        # If there are no (valid) credentials available, let the user log in.
        if not creds or not creds.valid:
            if creds and creds.expired and creds.refresh_token:
                creds.refresh(Request())
            else:
                flow = InstalledAppFlow.from_client_secrets_file(
                    'credentials.json', scopes)
                creds = flow.run_local_server(port=0)
            # Save the credentials for the next run
            with open('token.json', 'w') as token:
                token.write(creds.to_json())
        self.creds = creds

    def read(self, read_range):
        try:
            service = build('sheets', 'v4', credentials=self.creds)
            # Call the Sheets API
            sheet = service.spreadsheets()
            result = sheet.values().get(spreadsheetId=self.spreadsheet_id,
                                        range=read_range).execute()
            values = result.get('values', [])
            text = ''
            if not values:
                # print('No data found.')
                return 'No data found.'
            print('Name, Major:')
            text += 'Name, Major:\n'
            for row in values:
                # Print columns A and E, which correspond to indices 0 and 4.
                # print('%s, %s' % (row[0], row[1]))
                text += '%s, %s' % (row[0], row[1]) + '\n'
            return text
        except HttpError as err:
            print(err)

    def app_end(self, values):
        try:
            service = build('Sheets', 'v4', credentials=self.creds)
            sheet = service.spreadsheets()
            added_range_address = sheet.values().append(
                spreadsheetId=self.spreadsheet_id,
                range=self.working_range,
                valueInputOption="USER_ENTERED",
                insertDataOption="INSERT_ROWS",
                body={"values": [values]}
            ).execute()["updates"]["updatedRange"]
            return added_range_address
        except HttpError as err:
            print(err)

    def clear(self, clear_range):
        try:
            service = build('Sheets', 'v4', credentials=self.creds)
            sheet = service.spreadsheets()
            return sheet.values().clear(
                spreadsheetId=self.spreadsheet_id,
                range=clear_range
            ).execute()
        except HttpError as err:
            print(err)

    def delete_rew(self):
        pass