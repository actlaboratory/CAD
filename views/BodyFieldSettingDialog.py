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

	def __init__(self, parent, key="", fieldType=_("固定値"), valueType="string", body=""):
		super().__init__(
			parent,
			[
				(_("フィールド名"), True),
				(_("タイプ"), (_("固定値"), _("編集可能"))),
				(_("型"), ("string","int","float","true","false","null")),
				(_("値"), True),
			],
			[None]*4,
			key, fieldType, valueType, body
		)

	def Initialize(self):
		super().Initialize(_("body"))
		self.edits[2].Bind(wx.EVT_COMBOBOX, self.onChangeType)
		return True

	def onChangeType(self, event):
		self.edits[3].Enable(self.edits[2].GetValue() in ("string","int","float"))

	def Validation(self,event):
		error = BodyField.validateName(self.edits[0].GetValue())
		if error:
			errorDialog(error, self.wnd)
			return

		error = BodyField.validateValueString(BodyFieldType[self.edits[1].GetStringSelection()], self.edits[2].GetValue(), self.edits[3].GetValue())
		if error:
			errorDialog(error, self.wnd)
			return
		event.Skip()

	def GetData(self):
		return [
			self.edits[0].GetValue().strip(),
			self.edits[1].GetStringSelection(),
			self.edits[2].GetStringSelection(),
			self.edits[3].GetValue().strip(),
		]

