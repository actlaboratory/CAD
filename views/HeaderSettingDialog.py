# -*- coding: utf-8 -*-
# ヘッダ設定ダイアログ
#Copyright (C) 2023-2025 yamahubuki <itiro.ishino@gmail.com>

import wx
import json

from .baseDialog import *
from entities import Header
from enumClasses import HeaderFieldType
from simpleDialog import errorDialog
from views.KeyValueSettingDialogBase import KeyValueSettingDialogBase, SettingDialogBase

class HeaderSettingDialog(BaseDialog):
	"""ヘッダの設定内容を入力するダイアログ"""

	def __init__(self, parent, key="", headerType=_("固定値"), body=""):
		super().__init__("valueSettingDialog")
		self.parent=parent
		self.values=[key,headerType,body]
		self.dialog = None

	def Initialize(self):
		super().Initialize(self.parent,_("ヘッダ設定"),style=wx.WS_EX_VALIDATE_RECURSIVELY|wx.DEFAULT_FRAME_STYLE)
		self.InstallControls()
		if self.isChoiceType():
			self.createDialog(json.loads(self.values[2]))
			self.valueEdit.SetValue("")
		return True

	def getAvailableHeaderTypeChoices(self):
		return (_("固定値"), _("編集可能"), _("固定値選択"), _("選択"))

	def InstallControls(self):
		"""いろんなwidgetを設置する。"""
		self.baseCreator=views.ViewCreator.ViewCreator(self.viewMode,self.panel,self.sizer,wx.VERTICAL,20,style=wx.ALL,margin=20)

		creator=views.ViewCreator.ViewCreator(self.viewMode,self.baseCreator.GetPanel(),self.baseCreator.GetSizer(),wx.HORIZONTAL,10)
		self.keyEdit,dummy=creator.inputbox(_("フィールド名"),x=500,defaultValue=self.values[0], textLayout=wx.VERTICAL)
		self.keyEdit.hideScrollBar(wx.HORIZONTAL)

		creator=views.ViewCreator.ViewCreator(self.viewMode,self.baseCreator.GetPanel(),self.baseCreator.GetSizer(),wx.HORIZONTAL,10)
		state = (_("固定値"), _("編集可能"), _("固定値選択"), _("選択")).index(self.values[1])
		self.headerTypeCombobox,dummy=creator.combobox(_("タイプ"),self.getAvailableHeaderTypeChoices(),state=state, x=500,textLayout=wx.VERTICAL)

		creator=views.ViewCreator.ViewCreator(self.viewMode,self.baseCreator.GetPanel(),self.baseCreator.GetSizer(),wx.HORIZONTAL,0)
		self.valueEdit,dummy=creator.inputbox(_("値"),x=500,defaultValue=self.values[2], textLayout=wx.VERTICAL)
		self.valueEdit.hideScrollBar(wx.HORIZONTAL)

		# 選択肢入力ボタン
		self.creator=views.ViewCreator.ViewCreator(self.viewMode,self.panel,self.sizer,wx.HORIZONTAL,20,"",wx.ALIGN_RIGHT, 10)
		self.valueInputButton=self.creator.button(_("選択肢入力"),self.ValueInput)

		#ボタンエリア
		self.creator=views.ViewCreator.ViewCreator(self.viewMode,self.panel,self.sizer,wx.HORIZONTAL,20,"",wx.ALIGN_RIGHT|wx.TOP, 10)
		self.bOk=self.creator.okbutton(_("ＯＫ"),self.Validation)
		self.bCancel=self.creator.cancelbutton(_("キャンセル"),None)

	def ValueInput(self, event):
		if not self.dialog:
			self.createDialog({})
		self.dialog.Initialize(self.wnd, _("ヘッダフィールド選択肢設定"))
		self.dialog.Show()

	def createDialog(self, values):
		self.dialog = HeaderChoiceDialog(
			"headerChoiceDialog",
			HeaderChoiceEditDialog,
			[
				("名称",0,200),
				(_("値"),0, 300)
			],
			values
		)

	def isChoiceType(self):
		return self.headerTypeCombobox.GetStringSelection() in [_("選択"),_("固定値選択")]

	def Validation(self,event):
		error = Header.validateName(self.keyEdit.GetValue())
		if error:
			errorDialog(error, self.wnd)
			return

		if not self.isChoiceType():
			error = Header.validateValue(HeaderFieldType[self.headerTypeCombobox.GetStringSelection()], self.valueEdit.GetValue())
			if error:
				errorDialog(error, self.wnd)
				return
		event.Skip()

	def GetData(self):
		return [
			self.keyEdit.GetValue().strip(),
			self.headerTypeCombobox.GetStringSelection(),
			json.dumps(self.dialog.GetValue()[0]) if self.isChoiceType() else self.valueEdit.GetValue().strip()
		]

class FixedHeaderSettingDialog(HeaderSettingDialog):
	def getAvailableHeaderTypeChoices(self):
		return (_("固定値"),)

class HeaderChoiceDialog(KeyValueSettingDialogBase):
	def OkButtonEvent(self, event):
		if len(self.values) == 0:
			errorDialog(_("１項目以上指定してください"), self.wnd)
			return
		event.Skip()

class HeaderChoiceEditDialog(SettingDialogBase):
	def __init__(self,parent,name="",value=""):
		super().__init__(
			parent,
			[
				(_("名称"),True),
				(_("値"),True)
			],
			[],
			name,
			value
		)

	def Initialize(self):
		super().Initialize(_("ヘッダ選択肢入力"))

	def Validation(self,event):
		error = Header.validateValue(HeaderFieldType.CONST, self.edits[1].GetValue())
		if error:
			errorDialog(error, self.wnd)
			return
		event.Skip()
