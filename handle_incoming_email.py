__author__ = 'ciacicode'

import logging
import webapp2
from google.appengine.ext.webapp.mail_handlers import InboundMailHandler
from google.appengine.api import mail


class LogSenderHandler(InboundMailHandler):
    def receive(self, mail_message):
        logging.info("Received a message from: " + mail_message.sender)
        file


app = webapp2.WSGIApplication([LogSenderHandler.mapping()], debug=True)
