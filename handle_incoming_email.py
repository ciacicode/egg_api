__author__ = 'ciacicode'

import logging
import webapp2
from uritools import uriencode
from google.appengine.ext.webapp.mail_handlers import InboundMailHandler
from oauth2client.client import GoogleCredentials
from googleapiclient.discovery import build
from googleapiclient import http
import cStringIO
import base64
from flask import jsonify
from modules.DBActions import add_receipt

credentials = GoogleCredentials.get_application_default()

def create_service():
    # Get the application default credentials.
    credentials = GoogleCredentials.get_application_default()

    # Construct the service object for interacting with the Cloud Storage API -
    return build('storage', 'v1', credentials=credentials)


class LogSenderHandler(InboundMailHandler):
    def receive(self, mail_message):
        sender = mail_message.sender
        # upload attachment to cloud storage
        filename = 'any'
        body = 'eny'
        try:
            attachment = mail_message.attachments
            filename = str(attachment[0].filename)
            body = str(attachment[0].payload)
            dec = base64.b64decode(body)
        except IndexError as e:
            print e

        pdffile = cStringIO.StringIO()
        pdffile.write(dec)
        media = http.MediaIoBaseUpload(pdffile, mimetype='application/pdf')
        storage = create_service()
        req = storage.objects().insert(bucket='ocadopdf', body={'name': filename, 'acl': [{'entity':'user-maria.cerase@gmail.com' ,'role': 'OWNER', 'email':'maria.cerase@gmail.com'}]}, media_body=media, projection='full')
        # file uploaded
        res = req.execute()
        # create response with media link and email of the user
        output = {'mediaLink': res['mediaLink'], 'email': str(sender)}
        response = jsonify(output)
        response.status_code = 201
        return response

app = webapp2.WSGIApplication([LogSenderHandler.mapping()], debug=True)
