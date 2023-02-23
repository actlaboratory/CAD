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

	def getStringValue(self):
		if self.getValue() is True:
			return "true"
		elif self.getValue() is False:
			return "false"
		elif self.getValue() is None:
			return "null"
		else:
			return str(self.getValue())

	def getValueTypeString(self):
		if self.getValue() is True:
			return "true"
		elif self.getValue() is False:
			return "false"
		elif self.getValue() is None:
			return "null"
		elif type(self.getValue()) == int:
			return "int"
		elif type(self.getValue()) == float:
			return "float"
		elif type(self.getValue()) == str:
			return "string"
		else:
			raise NotImplementedError()

	def getValue(self):
		return self.value


def generateFromString(name, fieldType, valueType, value=""):
	if valueType == "string":
		return BodyField(name, BodyFieldType[fieldType], value)
	elif valueType == "int":
		return BodyField(name, BodyFieldType[fieldType], int(value))
	elif valueType == "float":
		return BodyField(name, BodyFieldType[fieldType], float(value))
	elif valueType == "true":
		return BodyField(name, BodyFieldType[fieldType], True)
	elif valueType == "false":
		return BodyField(name, BodyFieldType[fieldType], False)
	elif valueType == "null":
		return BodyField(name, BodyFieldType[fieldType], None)
	else:
		raise ValueError("invalid valueType")


def validateName(name):
	assert isinstance(name, str)
	name = name.strip()
	if not len(name):
		return _("名前を入力してください。")
	return ""

def validateValue(fieldType, value):
	assert isinstance(value, (str,int, float, bool, type(None)))
	return ""

def validateValueString(fieldType, valueType, value):
	assert type(valueType) == str

	if fieldType == BodyFieldType.EDITABLE and valueType in ("true", "false", "null"):
		return _("true・false・nullを編集可能に設定することはできません。")

	if valueType == "int":
		assert type(value) == str
		try:
			v = int(value)
		except:
			return _("int型に変換できない値です。")

	elif valueType == "float":
		assert type(value) == str
		try:
			v = float(value)
		except:
			return _("float型に変換できない値です。")
	elif valueType == "string":
		assert type(value) == str

	return ""

def validateFieldType(fieldType):
	assert isinstance(fieldType, BodyFieldType)
