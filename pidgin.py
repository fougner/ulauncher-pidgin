import dbus
import logging

logger = logging.getLogger(__name__)

class Buddy():
    def __init__(self, id, name, alias):
        self.id = id
        self.name = name
        self.alias = alias

    def setAccount(self, account):
        self.account = account

    def getAccount(self):
        return self.account

class Pidgin():

    buddies = None

    @property
    def _bus(self):
        return dbus.SessionBus().get_object("im.pidgin.purple.PurpleService", "/im/pidgin/purple/PurpleObject")

    @property
    def _interface(self):
        return dbus.Interface(self._bus, 'im.pidgin.purple.PurpleInterface')

    def getBuddies(self):
        if not self.buddies:
            self._updateBuddies()
        return self.buddies

    def _updateBuddies(self):
        self.buddies = []
        for account in self._interface.PurpleAccountsGetAllActive():
            logger.debug("accounttype: " + str(type(account)))

            for buddyId in self._interface.PurpleFindBuddies(int(account), ""):
                b = Buddy(buddyId, self._getName(buddyId), self._getAlias(buddyId))
                b.setAccount(account)
                self.buddies.append(b)

    def _getName(self, buddy):
        name = self._interface.PurpleBuddyGetName(buddy)
        return str(name)

    def _getAlias(self, buddy):
        alias = self._interface.PurpleBuddyGetAlias(buddy)
        return str(alias)

    def newConversation(self, account, name):
        self._interface.PurpleConversationNew(1, account, name)