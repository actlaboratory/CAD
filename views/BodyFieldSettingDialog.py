# -*- coding: utf-8 -*-
# body設定ダイアログ
#Copyright (C) 2023 yamahubuki <itiro.ishino@gmail.com>

import wx

import views.KeyValueSettingDialogBase

from entities import BodyField
from enumClasses import BodyFieldType
from simpleDialog import errorDialog


class BodyFieldSettingDialog(views.KeyValueSettingDialogBase.SettingDialogBase):
	"""Bodyの設定内容を入力するダイアログ"""

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
		return super().Initialize(_("body"))

	def Validation(self,event):
		error = BodyField.validateName(self.edits[0].GetValue())
		if error:
			errorDialog(error, self.wnd)
			return

		error = BodyField.validateValue(BodyFieldType[self.edits[1].GetStringSelection()], self.edits[2].GetValue())
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

