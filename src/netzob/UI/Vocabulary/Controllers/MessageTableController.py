# -*- coding: utf-8 -*-

#+---------------------------------------------------------------------------+
#|          01001110 01100101 01110100 01111010 01101111 01100010            |
#|                                                                           |
#|               Netzob : Inferring communication protocols                  |
#+---------------------------------------------------------------------------+
#| Copyright (C) 2011 Georges Bossert and Frédéric Guihéry                   |
#| This program is free software: you can redistribute it and/or modify      |
#| it under the terms of the GNU General Public License as published by      |
#| the Free Software Foundation, either version 3 of the License, or         |
#| (at your option) any later version.                                       |
#|                                                                           |
#| This program is distributed in the hope that it will be useful,           |
#| but WITHOUT ANY WARRANTY; without even the implied warranty of            |
#| MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the              |
#| GNU General Public License for more details.                              |
#|                                                                           |
#| You should have received a copy of the GNU General Public License         |
#| along with this program. If not, see <http://www.gnu.org/licenses/>.      |
#+---------------------------------------------------------------------------+
#| @url      : http://www.netzob.org                                         |
#| @contact  : contact@netzob.org                                            |
#| @sponsors : Amossys, http://www.amossys.fr                                |
#|             Supélec, http://www.rennes.supelec.fr/ren/rd/cidre/           |
#+---------------------------------------------------------------------------+

#+----------------------------------------------
#| Global Imports
#+----------------------------------------------
from gi.repository import Gdk
import logging

#+---------------------------------------------------------------------------+
#| Local application imports
#+---------------------------------------------------------------------------+
from netzob.UI.Vocabulary.Views.MessageTableView import MessageTableView
from netzob.UI.Vocabulary.Controllers.Menus.ContextualMenuOnFieldController import ContextualMenuOnFieldController


class MessageTableController(object):

    def __init__(self, vocabularyPerspective):
        self.vocabularyPerspective = vocabularyPerspective
        self._view = MessageTableView(self)
        self.selectedMessages = []

    @property
    def view(self):
        return self._view

    def getSelectedMessages(self):
        return self.selectedMessages

    def messageTableTreeView_changed_event_cb(self, selection):
        """Callback executed when the user
        clicks on a message in the MessageTable"""

        if self.vocabularyPerspective.controller.selectedMessagesToMove is not None:
            self.vocabularyPerspective.controller.removePendingMessagesToMove()

        self.selectedMessages = []
        if selection is not None:
            (model, rows) = selection.get_selected_rows()
            for row in rows:
                iter = model.get_iter(row)
                msgID = model[iter][0]
                if msgID is not None:
                    message = self.vocabularyPerspective.getCurrentProject().getVocabulary().getMessageByID(msgID)
                    if message is None:
                        logging.warn("Impossible to retrieve the requested message ({0})".format(msgID))
                    else:
                        self.selectedMessages.append(message)
            self.vocabularyPerspective.updateMessageProperties()
            return
        self.selectedMessages = []
        self.vocabularyPerspective.updateMessageProperties()

    def messageListBox_button_press_event_cb(self, box, eventButton):
        self.vocabularyPerspective.setSelectedMessageTable(self.view)

    def closeButton_clicked_cb(self, button):
        self.vocabularyPerspective.removeMessageTable(self.view)

    def messageTableTreeView_button_press_event_cb(self, treeview, eventButton):
        self.vocabularyPerspective.setSelectedMessageTable(self.view)
        # Popup a contextual menu if right click
        if eventButton.type == Gdk.EventType.BUTTON_PRESS and eventButton.button == 3:
            x = int(eventButton.x)
            y = int(eventButton.y)
            try:
                (path, treeviewColumn, x, y) = treeview.get_path_at_pos(x, y)
            except:
                # No message selected
                return

            # Retrieve the selected message
            symbol = self._view.getDisplayedSymbol()
            if symbol is None:
                logging.warn("No symbol is selected, please choose one.")
                return

            message_id = None
            aIter = treeview.get_model().get_iter(path)
            if aIter and treeview.get_model().iter_is_valid(aIter):
                message_id = treeview.get_model().get_value(aIter, 0)
                message = symbol.getMessageByID(message_id)
            else:
                logging.warn(_("Impossible to retrieve the clicked message !"))
                return

            # Retrieve the selected field number
            iField = 0
            for col in treeview.get_columns():
                if col == treeviewColumn:
                    break
                iField += 1
            field = symbol.getFieldByIndex(iField)
            if field is None:
                logging.warn(_("Impossible to retrieve the clicked field !"))
                return

            # Popup a contextual menu
            menuController = ContextualMenuOnFieldController(self.vocabularyPerspective.controller, symbol, message, field)
            menuController.run(eventButton)

    def messageTableTreeView_enter_notify_event_cb(self, treeView, data=None):
        self.view.treeViewHeaderGroup.setAllColumnsFocus(True)

    def messageTableTreeView_leave_notify_event_cb(self, treeView, data=None):
        self.view.treeViewHeaderGroup.setAllColumnsFocus(False)

    def messageTableBox_enter_notify_event_cb(self, treeView, data=None):
        self.view.treeViewHeaderGroup.setAllColumnsFocus(True)

    def messageTableBox_leave_notify_event_cb(self, treeView, data=None):
        self.view.treeViewHeaderGroup.setAllColumnsFocus(False)