# -*- coding: utf-8 -*-
# URIフィールドエンティティ
#Copyright (C) 2023 yamahubuki <itiro.ishino@gmail.com>

from enumClasses import UriFieldType

class UriField:
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
	return ""

def validateValue(fieldType, value):
	assert isinstance(value, str)
	value = value.strip()
	if fieldType != UriFieldType.EDITABLE and not len(value):
		return _("値を入力してください");
	return ""

def validateFieldType(fieldType):
	assert isinstance(fieldType, UriFieldType)
