# -*- coding: utf-8 -*-
# サービスプロバイダ一覧ダイアログ
#Copyright (C) 2023 yamahubuki <itiro.ishino@gmail.com>

import wx
import wx.lib.scrolledpanel

import menuItemsStore
import simpleDialog
import views.ViewCreator

from dao.ServiceProviderDao import ServiceProviderDao

from entities import ServiceProvider
from enumClasses import ContentType

from simpleDialog import errorDialog
from views.baseDialog import *
from views.EndpointDialog import *
from views.ServiceProviderEditDialog import *


class Dialog(BaseDialog):
	def __init__(self):
		super().__init__("ServiceProviderDialog")
		self.lst = self.load()
		self.result = None

	def Initialize(self, parent=None):
		self.log.debug("created")
		if parent == None:
			parent = self.app.hMainView.hFrame
		super().Initialize(parent,_("サービスプロバイダ一覧"))
		self.InstallControls()
		return True

	def InstallControls(self):
		self.creator = views.ViewCreator.ViewCreator(self.viewMode,self.panel,self.sizer,wx.VERTICAL,20,style=wx.LEFT|wx.RIGHT|wx.TOP|wx.EXPAND,margin=20)
		(self.list,dummy) = self.creator.virtualListCtrl(_("設定中のプロバイダ"), size=(600,400))
		self.list.AppendColumn(_("サービス名"), width=300)
		self.list.AppendColumn(_("メモ"), width=300)
		self.list.setList(self.lst)
		self.list.Bind(wx.EVT_LIST_ITEM_ACTIVATED,self.onActivate)
		self.list.Bind(wx.EVT_LIST_ITEM_SELECTED,self.ItemSelected)
		self.list.Bind(wx.EVT_LIST_ITEM_DESELECTED,self.ItemSelected)

		creator=views.ViewCreator.ViewCreator(self.viewMode,self.panel,self.sizer,wx.HORIZONTAL,20,style=wx.ALIGN_RIGHT)
		self.addButton = creator.button(_("追加(&A)"), self.add)
		self.editButton = creator.button(_("編集(&E)"), self.edit)
		self.deleteButton = creator.button(_("削除(&D)"), self.delete)

		creator=views.ViewCreator.ViewCreator(self.viewMode,self.panel,self.sizer,wx.HORIZONTAL,20,style=wx.TOP|wx.BOTTOM|wx.ALIGN_RIGHT)
		self.bClose=creator.closebutton(_("閉じる(&C)"),None)

		self.ItemSelected()

		keymap = self.app.hMainView.menu.keymap
		keymap.Set(self.identifier,self.wnd,self.onKey)

	def ItemSelected(self,event=None):
		self.editButton.Enable(self.list.GetFocusedItem()>=0)
		self.deleteButton.Enable(self.list.GetFocusedItem()>=0)

	def activate(self, target):
		d = EndpointDialog()
		d.Initialize(target, self)
		if d.Show() == wx.ID_EXECUTE:
			self.result = d.GetValue()
			self.wnd.EndModal(wx.ID_EXECUTE)

	def add(self, event=None):
		d = ServiceProviderEditDialog()
		d.Initialize(ServiceProvider.ServiceProvider(_("新規プロバイダ"), ContentType.JSON), self.wnd)
		if d.Show() == wx.ID_OK:
			self.list.Append(d.GetValue())
			self.save()

	def edit(self, event=None):
		index = self.list.GetFocusedItem()
		if index < 0:
			return
		target = self.lst[index]
		d = ServiceProviderEditDialog()
		d.Initialize(target, self.wnd)
		result = d.Show()
		if result == wx.ID_OK:
			self.list[index] = target.updateEdit(d.GetValue())
			self.save()

	def delete(self, event=None):
		index = self.list.GetFocusedItem()
		if index < 0:
			return
		target = self.lst[index]

		if simpleDialog.yesNoDialog(_("削除の確認"), _("%sを削除しますか？" % target.getName()), self.wnd) == wx.ID_YES:
			self.list.DeleteItem(index)
			self.save()

	def save(self):
		try:
			ServiceProviderDao.saveAll(self.lst)
		except Exception as e:
			errorDialog(_("保存に失敗しました。\n\n") + str(e))

	def load(self):
		try:
			return ServiceProviderDao.loadAll()
		except Exception as e:
			errorDialog(_("読込に失敗しました。\n\n") + str(e))
			return []

	def onActivate(self, event):
		index = self.list.GetFocusedItem()
		if index < 0:
			return
		self.activate(self.lst[index])

	def onKey(self, event):
		selected=event.GetId()#メニュー識別しの数値
		index = self.list.GetFocusedItem()
		if selected==menuItemsStore.getRef("ADD"):
			self.add()
			return
		elif index>=0:
			if selected==menuItemsStore.getRef("ACTIVATED"):
				self.activate(self.lst[index])
			elif selected==menuItemsStore.getRef("DELETE"):
				self.delete()
				return
			elif selected==menuItemsStore.getRef("EDIT"):
				self.edit()
				return
		event.Skip()

	def GetData(self):
		return self.result
