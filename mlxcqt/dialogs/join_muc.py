import asyncio

import aioxmpp

import jclib.identity

from .. import Qt, models, utils

from ..ui import dlg_join_muc


class JoinMuc(Qt.QDialog):
    def __init__(self, accounts: jclib.identity.Account, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.ui = dlg_join_muc.Ui_DlgJoinMUC()
        self.ui.setupUi(self)

        self.base_model = models.AccountsModel(accounts)
        self.ui.account.setModel(self.base_model)

        self._jid_validator = utils.JIDValidator()

        self.ui.mucjid.setValidator(self._jid_validator)
        self.ui.mucjid.editingFinished.connect(
            self._mucjid_edited
        )

    def _mucjid_edited(self):
        jid = aioxmpp.JID.fromstr(self.ui.mucjid.text())
        if jid.resource and not self.ui.nickname.text():
            self.ui.nickname.setText(jid.resource)
            self.ui.mucjid.setText(str(jid.bare()))

    def done(self, r):
        if r != Qt.QDialog.Accepted:
            return super().done(r)

        # TODO: produce proper error messages here
        if not self.ui.mucjid.hasAcceptableInput():
            return

        jid = aioxmpp.JID.fromstr(self.ui.mucjid.text())
        if not jid.is_bare:
            return

        if not self.ui.account.currentAccount():
            return

        if not self.ui.nickname.text():
            return

        return super().done(r)

    @asyncio.coroutine
    def run(self):
        result = yield from utils.exec_async(self)
        if result != Qt.QDialog.Accepted:
            return None

        account = self.ui.account.currentAccount()

        return (account,
                aioxmpp.JID.fromstr(self.ui.mucjid.text()),
                self.ui.nickname.text())
