# -*- coding: utf-8 -*-
# ヘッダ設定ダイアログ
#Copyright (C) 2023-2024 yamahubuki <itiro.ishino@gmail.com>

import wx

from .baseDialog import *
from entities import Header
from enumClasses import HeaderFieldType
from simpleDialog import errorDialog


class HeaderSettingDialog(BaseDialog):
	"""ヘッダの設定内容を入力するダイアログ"""

	def __init__(self, parent, key="", headerType=_("固定値"), body=""):
		super().__init__("valueSettingDialog")
		self.parent=parent
		self.values=[key,headerType,body]

	def Initialize(self):
		super().Initialize(self.parent,_("ヘッダ設定"),style=wx.WS_EX_VALIDATE_RECURSIVELY|wx.DEFAULT_FRAME_STYLE)
		self.InstallControls()
		return True

	def InstallControls(self):
		"""いろんなwidgetを設置する。"""
		self.baseCreator=views.ViewCreator.ViewCreator(self.viewMode,self.panel,self.sizer,wx.VERTICAL,20,style=wx.ALL,margin=20)

		creator=views.ViewCreator.ViewCreator(self.viewMode,self.baseCreator.GetPanel(),self.baseCreator.GetSizer(),wx.HORIZONTAL,10)
		self.keyEdit,dummy=creator.inputbox(_("フィールド名"),x=500,defaultValue=self.values[0], textLayout=wx.VERTICAL)
		self.keyEdit.hideScrollBar(wx.HORIZONTAL)

		creator=views.ViewCreator.ViewCreator(self.viewMode,self.baseCreator.GetPanel(),self.baseCreator.GetSizer(),wx.HORIZONTAL,10)
		state = (_("固定値"), _("編集可能")).index(self.values[1])
		self.headerTypeCombobox,dummy=creator.combobox(_("タイプ"),(_("固定値"), _("編集可能")),state=state, x=500,textLayout=wx.VERTICAL)

		creator=views.ViewCreator.ViewCreator(self.viewMode,self.baseCreator.GetPanel(),self.baseCreator.GetSizer(),wx.HORIZONTAL,10)
		self.valueEdit,dummy=creator.inputbox(_("値"),x=500,defaultValue=self.values[2], textLayout=wx.VERTICAL)
		self.valueEdit.hideScrollBar(wx.HORIZONTAL)

		#ボタンエリア
		self.creator=views.ViewCreator.ViewCreator(self.viewMode,self.panel,self.sizer,wx.HORIZONTAL,20,"",wx.ALIGN_RIGHT|wx.TOP, 10)
		self.bOk=self.creator.okbutton(_("ＯＫ"),self.Validation)
		self.bCancel=self.creator.cancelbutton(_("キャンセル"),None)

	def Validation(self,event):
		error = Header.validateName(self.keyEdit.GetValue())
		if error:
			errorDialog(error, self.wnd)
			return

		error = Header.validateValue(HeaderFieldType[self.headerTypeCombobox.GetStringSelection()], self.valueEdit.GetValue())
		if error:
			errorDialog(error, self.wnd)
			return
		event.Skip()

	def GetData(self):
		return [
			self.keyEdit.GetValue().strip(),
			self.headerTypeCombobox.GetStringSelection(),
			self.valueEdit.GetValue().strip()
		]
