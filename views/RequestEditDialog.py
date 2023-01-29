# -*- coding: utf-8 -*-
# リクエスト設定ダイアログ
#Copyright (C) 2023 yamahubuki <itiro.ishino@gmail.com>

import urllib.parse
import wx

import views.ViewCreator

from urllib3.util.url import parse_url

from entities import BodyField, Endpoint, Header, Request, UriField
from enumClasses import BodyFieldType, ContentType, HeaderFieldType, Method, UriFieldType
from simpleDialog import errorDialog
from views.baseDialog import *


class RequestEditDialog(BaseDialog):
	def __init__(self):
		super().__init__("RequestDialog")

	def InitializeFromEndpoint(self, parent, provider, endpoint):
		super().Initialize(parent.wnd,_("リクエスト内容編集"))
		self.parent = parent
		self.provider = provider
		self.endpoint = endpoint
		self.log.debug("created with" + provider.getName() and endpoint.getName())

		# デフォルトの定義
		defaults = {
			"name" : "%s(%s)" % (self.endpoint.getName(),self.provider.getName()),
			"baseUris" : provider.getBaseUris(),
			"contentType" : endpoint.getContentType() if endpoint.getContentType() else provider.getContentType(),
			"headers" : [],	# この後追加
			"method" : endpoint.getMethod(),
			"uri" : endpoint.getUri(),
			"uriFields" : endpoint.getUriFields(),
			"body" : endpoint.getBody(),
			
		}

		# ヘッダをエンドポイント優先で追加
		tmp = []
		for i in endpoint.getAditionalHeaders():
			if i.getName() not in tmp:
				tmp.append(i.getName())
				defaults["headers"].append(i)
		for i in provider.getHeaders():
			if i.getName() not in tmp:
				tmp.append(i.getName())
				defaults["headers"].append(i)

		self.InstallControls(defaults)
		return True

	def InstallControls(self, defaults):
		# 画面をスクロール可能にする
		panel = wx.lib.scrolledpanel.ScrolledPanel(self.panel,wx.ID_ANY, size=(850,500))
		creator=views.ViewCreator.ViewCreator(self.viewMode,panel,None,wx.VERTICAL,20,style=wx.ALL|wx.EXPAND,margin=20)
		sizer = creator.GetSizer()
		self.sizer.Add(panel,1,wx.EXPAND)

		grid=views.ViewCreator.ViewCreator(self.viewMode,panel,sizer,views.ViewCreator.FlexGridSizer,20,2)

		# 名前　いったん固定
		self.name, dummy = grid.inputbox(_("名前"), None, defaults["name"], wx.BORDER_RAISED, 400, sizerFlag=wx.ALL|wx.EXPAND)
		self.name.hideScrollBar(wx.HORIZONTAL)
		self.name.SetMaxSize((600,200))
		if defaults["name"]:
			self.name.Hide()

		# URI
		self.uri, dummy = grid.inputbox(_("URI"), None, defaults["uri"], wx.BORDER_RAISED, 400, sizerFlag=wx.ALL|wx.EXPAND)
		self.uri.hideScrollBar(wx.HORIZONTAL)
		if defaults["baseUris"]:
			self.uri.Hide()
			# ベースURI
			self.baseUris, dummy = grid.combobox(_("ベースURI"), ["%s (%s)" %(item.getName(),item.getAddress()) for item in defaults["baseUris"]], state=0)
			self.baseUris.SetMaxSize((600,200))
		else:
			self.baseUris = None

		# method
		state = 0
		if defaults["method"]:
			state = defaults["method"].value
		self.method, dummy = grid.combobox(_("メソッド"), [item.name for item in Method], None, state=state)
		if defaults["method"] is not None:
			self.method.Hide()

		# contentType
		state = 0
		if defaults["contentType"]:
			state = defaults["contentType"].value
		self.contentType, dummy = grid.combobox(_("通信形式"), ["application/json","application/x-www-form-urlencoded"], None, state=state)
		if defaults["contentType"] is not None:
			self.contentType.Hide()

		# ヘッダ
		self.headers = {}
		for item in defaults["headers"]:
			if item.getFieldType() == HeaderFieldType.CONST:
				self.headers[item.getName()] = item.getValue()
			elif item.getFieldType() == HeaderFieldType.EDITABLE:
				form,dummy = grid.inputbox(_("%sヘッダ" % item.getName()), None, item.getValue(), wx.BORDER_RAISED, 400, sizerFlag=wx.ALL|wx.EXPAND)
				form.hideScrollBar(wx.HORIZONTAL)
				self.headers[item.getName()] = form
			else:
				raise NotImplementedError()
	
		# URIフィールド
		self.uriFields = {}
		for item in defaults["uriFields"]:
			if item.getFieldType() == UriFieldType.EDITABLE:
				form,dummy = grid.inputbox(item.getName(), None, item.getValue(), wx.BORDER_RAISED, 400, sizerFlag=wx.ALL|wx.EXPAND)
				form.hideScrollBar(wx.HORIZONTAL)
				self.uriFields[item.getName()] = form
			else:
				raise NotImplementedError()

		# body
		self.body = {}
		for item in defaults["body"]:
			if item.getFieldType() == BodyFieldType.CONST:
				self.body[item.getName()] = item.getValue()
			elif item.getFieldType() == BodyFieldType.EDITABLE:
				form,dummy = grid.inputbox(item.getName(), None, item.getValue(), wx.BORDER_RAISED, 400, sizerFlag=wx.ALL|wx.EXPAND)
				form.hideScrollBar(wx.HORIZONTAL)
				self.body[item.getName()] = form
			else:
				raise NotImplementedError()

		hCreator=views.ViewCreator.ViewCreator(self.viewMode,self.panel,self.sizer,wx.HORIZONTAL,20,style=wx.ALL|wx.ALIGN_RIGHT,margin=20)
		okButton=hCreator.okbutton(_("OK"), self.processEnter)
		cancelButton=hCreator.cancelbutton(_("キャンセル"))

		panel.SetupScrolling()

	def processEnter(self, event):
		error = Request.validateName(self.name.GetValue())
		if error:
			errorDialog(error, self.wnd)
			return

		error = Endpoint.validateUri(self.uri.GetValue())
		if error:
			errorDialog(error, self.wnd)
			return

		for k,v in self.headers.items():
			if type(v) != str:
				error = Header.validateValue(HeaderFieldType.CONST, v.GetValue())
				if error:
					errorDialog(error, self.wnd)
					return

		for k,v in self.uriFields.items():
			if type(v) != str:
				error = UriField.validateValue(None, v.GetValue())
				if error:
					errorDialog(error, self.wnd)
					return

		for k,v in self.body.items():
			if type(v) != str:
				error = BodyField.validateValue(BodyFieldType.CONST, v.GetValue())
				if error:
					errorDialog(error, self.wnd)
					return

		self.wnd.EndModal(wx.ID_OK)


	def GetData(self):
		if self.baseUris:
			baseUri = self.provider.getBaseUris()[self.baseUris.GetSelection()]
			try:
				base = parse_url(baseUri.getAddress())
				endpoint = parse_url(self.uri.GetValue())
				if endpoint.scheme:
					uri = self.uri.GetValue()
				else:
					uri = baseUri.getAddress().rstrip("/")
					if endpoint.path:
						uri += "/"
					uri += self.uri.GetValue().lstrip("/")
			except:
				raise ValueError("validation bug found!")
		else:
			uri = self.uri.GetValue()

		#URIにUriFieldsを適用
		for k,v in self.uriFields.items():
			if type(v) != str:
				v=v.GetValue()
			uri = uri.replace("{"+k+"}", urllib.parse.quote(v))

		headers = []
		for k,v in self.headers.items():
			if type(v) == str:
				headers.append(Header.Header(k, HeaderFieldType.CONST, v))
			else:
				headers.append(Header.Header(k, HeaderFieldType.CONST, v.GetValue()))

		body = []
		for k,v in self.body.items():
			if type(v) == str:
				body.append(BodyField.BodyField(k, BodyFieldType.CONST, v))
			else:
				body.append(BodyField.BodyField(k, BodyFieldType.CONST, v.GetValue()))

		return Request.Request(
			self.name.GetValue(),
			ContentType(self.contentType.GetSelection()),
			Method(self.method.GetSelection()),
			uri,
			headers,
			body
		).toRequests()

