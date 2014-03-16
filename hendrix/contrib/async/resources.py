from twisted.internet.protocol import Factory, Protocol
from txsockjs.factory import SockJSResource
from .messaging import hxdispatcher

import json
import uuid

class MessageHandlerProtocol(Protocol):
    """
        A basic protocol for socket messaging 
        using a hendrix messaging dispatcher to handle
        addressing messages to active sockets from
        differnt contexts
    """
    dispatcher = hxdispatcher
    guid = None

    def dataReceived(self, data):


        """
            Takes "data" which we assume is json encoded
            If data has a subject_id attribute, we pass that to the dispatcher
            as the subject_id so it will get carried through into any 
            return communications and be identifiable to the client

            falls back to just passing the message along...

        """

        try:
            address = self.guid
            data = json.loads(data)

            if 'action' in data:
                return self.dispatcher.do_action(self.transport, data)

            if 'address' in data:
                address = data['address']
            else:
                address = self.guid

            self.dispatcher.send(address, data)

        except Exception, exc:
            raise
            self.dispatcher.send(self.guid, {'message':data, 'error':str(exc)})

    def connectionMade(self):
        """
            establish the address of this new connection and add it to the list of 
            sockets managed by the dispatcher

            TODO:
                a method that would put this transport in multiple channels
                based on current page, user group participation, activity or other such concerns
        """
        self.transport.uid = str(uuid.uuid1())

        self.guid = self.dispatcher.add(self.transport)
        self.dispatcher.send(self.guid, {'setup_connection':self.guid})


    def connectionLost(self, something):
        """
            clean up the no longer useful socket in the dispatcher
        """
        self.dispatcher.remove(self.transport)


def get_MessageHandler():
    """
        create an instance of the SockJSResource for use 
        as a child to the main wsgi app
    """

    return SockJSResource(Factory.forProtocol(MessageHandlerProtocol))
