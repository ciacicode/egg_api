__author__ = 'ciacicode'

import logging
import webapp2
import os
import cloudstorage as gcs
from google.appengine.ext.webapp.mail_handlers import InboundMailHandler
from google.appengine.api import mail


class LogSenderHandler(InboundMailHandler):
    def receive(self, mail_message):
        logging.info("Received a message from: " + mail_message.sender)
        # upload attachment to cloud storage
        attachment = mail_message.attachments
        print attachment
        content = attachment[0]
        print type(content)
        print content
        #for property, value in vars(content).iteritems():
            #print property, ": ", value
        





app = webapp2.WSGIApplication([LogSenderHandler.mapping()], debug=True)
