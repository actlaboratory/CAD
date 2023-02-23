# -*- coding: utf-8 -*-
# フィールドエンティティ
#Copyright (C) 2023 yamahubuki <itiro.ishino@gmail.com>

from enumClasses import BodyFieldType

class BodyField:
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
	assert isinstance(value, (str,int, float, bool, type(None)))
	return ""

def validateFieldType(fieldType):
	assert isinstance(fieldType, BodyFieldType)
