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
        for item in attachment:
            for prop, val in vars(item).iteritems():
                print prop, ": ", val






app = webapp2.WSGIApplication([LogSenderHandler.mapping()], debug=True)
