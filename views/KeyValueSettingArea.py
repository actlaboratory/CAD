# -*- coding: utf-8 -*-
# Key-Value setting area
#Copyright (C) 2022 yamahubuki <itiro.ishino@gmail.com>

import wx
import views.KeyValueSettingDialogBase

class KeyValueSettingArea(views.KeyValueSettingDialogBase.KeyValueSettingDialogBase):
	def Initialize(self,wnd, creator, title):
		self.wnd = wnd
		self.creator = creator
		self.InstallControls(title)
		self.initialized=True
		return True

