# -*- coding: utf-8 -*-
# フィールドエンティティ
#Copyright (C) 2023 yamahubuki <itiro.ishino@gmail.com>


class BodyField:
	def __init__(self, name, fieldType,value):
		if validateName(name) or validateFieldType(fieldType) or validateValue(value):
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

def validateValue(value):
	assert isinstance(value, str)
	value = value.strip()
	if not len(value):
		return _("名前を入力してください");
	return ""

def validateFieldType(fieldType):
	assert isinstance(fieldType, HeaderFieldType)
