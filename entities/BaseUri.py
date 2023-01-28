# -*- coding: utf-8 -*-
# ベースURIエンティティ
#Copyright (C) 2023 yamahubuki <itiro.ishino@gmail.com>

from urllib3.util.url import parse_url

ADDRESS_MIN_LENGTH = 10

class BaseUri:
	def __init__(self, name, address, port):
		if validateName(name) or validateAddress(address) or validatePort(port):
			raise ValueError()
		self.name = name.strip()
		self.address = address.strip()
		self.port = port.strip()

	def getAddress(self):
		return self.address

	def getName(self):
		return self.name

	def getPort(self):
		return self.port

def validateName(name):
	assert isinstance(name, str)
	name = name.strip()
	if not len(name):
		return _("名前を入力してください");
	return ""

def validateAddress(address):
	assert isinstance(address, str)
	address = address.strip()
	if len(address) < ADDRESS_MIN_LENGTH:
		return _("アドレスを%d文字以上で入力してください" % ADDRESS_MIN_LENGTH)
	if not address.startswith("https://") and not address.startswith("http://"):
		return _("アドレスはhttps://またはhttp://で始まる必要があります。")
	try:
		url = parse_url(address)
		if not url.scheme:
			return _("アドレスが不正です。")
		elif url.auth:
			return _("認証情報はアドレスではなくAuthorizationヘッダで指定してください。")
		elif not url.host:
			return _("アドレスにホスト名が含まれていません。")
		elif url.port:
			return _("ポート番号はアドレスではなく専用の入力欄で指定してください。")
		elif url.query:
			return _("ベースURLでクエリを指定することはできません。クエリはエンドポイントの設定時に指定してください。")
		elif url.fragment:
			return _("ベースURLでフラグメントを指定することはできません。フラグメントはエンドポイントの設定時に指定してください。")
	except:
		import traceback
		traceback.print_exc()
		return _("アドレスが不正です。")
	return ""

def validatePort(port):
	assert isinstance(port, str)
	port = port.strip()
	if len(port) == 0 or not port.isdigit():
		return _("ポート番号を数値で指定してください。")
	if int(port) <= 0 or int(port) > 65535:
		return _("ポート番号が不正です。")
	return ""
