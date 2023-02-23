# -*- coding: utf-8 -*-
# ヘッダエンティティ
#Copyright (C) 2023 yamahubuki <itiro.ishino@gmail.com>

from enumClasses import ContentType, HeaderFieldType

class Header:
	def __init__(self, name, fieldType,value):
		if validateName(name) or validateFieldType(fieldType) or validateValue(fieldType, value):
			raise ValueError()
		self.name = name
		self.fieldType = fieldType
		self.value = value

	def getName(self):
		return self.name

	def getFieldType(self):
		return self.fieldType

	def getValue(self):
		return self.value


def validateName(name):
	assert isinstance(name, str)
	name = name.strip()
	if not len(name):
		return _("名前を入力してください。")
	for c in name.encode("utf-8"):
		if c < 0x20 or c >= 0x7f:	#印字可能なASCII文字のみ使用可能
			return _("使用できない文字が含まれています。")
	return ""

def validateValue(fieldType, value):
	assert isinstance(value, str)
	value = value.strip()
	if fieldType == HeaderFieldType.REMOVE and value:
		return _("削除の場合は価を入力しないでください。")
	return ""

def validateFieldType(fieldType):
	assert isinstance(fieldType, HeaderFieldType)
