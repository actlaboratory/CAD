# -*- coding: utf-8 -*-
# ヘッダ設定ダイアログ
#Copyright (C) 2023 yamahubuki <itiro.ishino@gmail.com>

import wx

import views.KeyValueSettingDialogBase

from entities import Header
from enumClasses import HeaderFieldType
from simpleDialog import errorDialog


class HeaderSettingDialog(views.KeyValueSettingDialogBase.SettingDialogBase):
	"""ヘッダの設定内容を入力するダイアログ"""

	def __init__(self, parent, key="", headerType=_("固定値"), body=""):
		super().__init__(
			parent,
			[
				(_("フィールド名"), True),
				(_("タイプ"), (_("固定値"), _("編集可能"))),
				(_("値"), True),
			],
			[None]*3,
			key,headerType,body
		)

	def Initialize(self):
		return super().Initialize(_("ヘッダ設定"))

	def Validation(self,event):
		error = Header.validateName(self.edits[0].GetValue())
		if error:
			errorDialog(error, self.wnd)
			return

		error = Header.validateValue(HeaderFieldType[self.edits[1].GetStringSelection()], self.edits[2].GetValue())
		if error:
			errorDialog(error, self.wnd)
			return
		event.Skip()

	def GetData(self):
		return [
			self.edits[0].GetValue().strip(),
			self.edits[1].GetStringSelection(),
			self.edits[2].GetValue().strip()
		]

