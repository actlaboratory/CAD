# -*- coding: utf-8 -*-
# Key-Value setting area
#Copyright (C) 2022-2023 yamahubuki <itiro.ishino@gmail.com>

import wx
import views.KeyValueSettingDialogBase

class KeyValueSettingArea(views.KeyValueSettingDialogBase.KeyValueSettingDialogBase):
	def Initialize(self,wnd, creator, title):
		self.wnd = wnd
		self.creator = creator
		self.InstallControls(title)
		self.initialized=True
		return True

	def Show(self,modal=True):
		raise NotImplementedError()

	def GetValue(self):
		"""
			本来はShow()で行われるself.valueの保存処理をここで行ってから本来処理を実施
		"""
		self.value = self.GetData()
		return super().GetValue()