import dbus
import inspect
import logging

from ulauncher.api.client.Extension import Extension
from ulauncher.api.client.EventListener import EventListener
from ulauncher.api.shared.event import KeywordQueryEvent, ItemEnterEvent
from ulauncher.api.shared.item.ExtensionSmallResultItem import ExtensionSmallResultItem
from ulauncher.api.shared.action.ExtensionCustomAction import ExtensionCustomAction
from ulauncher.api.shared.action.RenderResultListAction import RenderResultListAction
from ulauncher.api.shared.action.HideWindowAction import HideWindowAction
from ulauncher.search.SortedList import SortedList

logger = logging.getLogger(__name__)
sessionBus = dbus.SessionBus()
purple = sessionBus.get_object("im.pidgin.purple.PurpleService", "/im/pidgin/purple/PurpleObject")
purple = dbus.Interface(purple, 'im.pidgin.purple.PurpleInterface')

class DemoExtension(Extension):

    def __init__(self):
        super(DemoExtension, self).__init__()
        self.subscribe(KeywordQueryEvent, KeywordQueryEventListener())
        self.subscribe(ItemEnterEvent, ItemEnterEventListener())

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

    def getBuddies():
        if not Pidgin.buddies:
            Pidgin.updateBuddies()
        return Pidgin.buddies

    def updateBuddies():
        Pidgin.buddies = []
        for account in purple.PurpleAccountsGetAllActive():
            logger.debug("accounttype: " + str(type(account)))

            for buddyId in purple.PurpleFindBuddies(int(account), ""):
                b = Buddy(buddyId, Pidgin.getName(buddyId), Pidgin.getAlias(buddyId))
                b.setAccount(account)
                Pidgin.buddies.append(b)

    def getName(buddy):
        name = purple.PurpleBuddyGetName(buddy)
        return str(name)

    def getAlias(buddy):
        alias = purple.PurpleBuddyGetAlias(buddy)
        return str(alias)

class ItemEnterEventListener(EventListener):

    def on_event(self, event, _extension):
        bud = event.get_data()
        purple.PurpleConversationNew(1, bud.account, bud.name)

class KeywordQueryEventListener(EventListener):

    def on_event(self, event, extension):
        query = event.get_argument()
        if not event.get_argument():
            query = ""
        items = SortedList(query, min_score=0, limit=9)
        for buddy in Pidgin.getBuddies():
            items.append(ExtensionSmallResultItem(icon='images/icon.png',
                                             name='%s' % buddy.alias,
                                             description='Account desc: %s' % buddy.name,
                                             on_enter=ExtensionCustomAction(buddy)))
        res = []
        for i in items:
            res.append(i)

        return RenderResultListAction(res)

if __name__ == '__main__':
    DemoExtension().run()