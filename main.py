import dbus
import inspect
import logging

from ulauncher.api.client.EventListener import EventListener
from ulauncher.api.client.Extension import Extension
from ulauncher.api.shared.action.ExtensionCustomAction import ExtensionCustomAction
from ulauncher.api.shared.action.HideWindowAction import HideWindowAction
from ulauncher.api.shared.action.RenderResultListAction import RenderResultListAction
from ulauncher.api.shared.event import KeywordQueryEvent, ItemEnterEvent
from ulauncher.api.shared.item.ExtensionResultItem import ExtensionResultItem
from ulauncher.api.shared.item.ExtensionSmallResultItem import ExtensionSmallResultItem
from ulauncher.search.SortedList import SortedList

from pidgin import Pidgin

logger = logging.getLogger(__name__)
pidgin = Pidgin()

class DemoExtension(Extension):

    def __init__(self):
        super(DemoExtension, self).__init__()
        self.subscribe(KeywordQueryEvent, KeywordQueryEventListener())
        self.subscribe(ItemEnterEvent, ItemEnterEventListener())

class ItemEnterEventListener(EventListener):

    def on_event(self, event, _extension):
        bud = event.get_data()
        pidgin.newConversation(bud.account, bud.name)

class KeywordQueryEventListener(EventListener):

    def on_event(self, event, extension):
        query = event.get_argument()
        if not event.get_argument():
            query = ""
        return self.render_results(query)

    def render_results(self, query):
        items = SortedList(query, min_score=0, limit=9)
        for buddy in pidgin.getBuddies():
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