# -*- coding: utf-8 -*-
# enum classes

import enum
from enum import IntEnum, EnumMeta, unique

class BodyFieldTypeEnumMeta(EnumMeta):
	def __getitem__(self, value):
		if value == _("固定値"):
			return super().__getitem__("CONST")
		elif value == _("編集可能"):
			return super().__getitem__("EDITABLE")
		if value == _("エンコード済み固定値"):
			return super().__getitem__("ENCORDED")
		else:
			return super().__getitem__(value)

@unique
class BodyFieldType(IntEnum, metaclass=BodyFieldTypeEnumMeta):
	CONST = 0
	EDITABLE = 1
	SELECT = 2
	ENCORDED = 3

	@property
	def view_name(self):
		"""The name of the Enum member."""
		if self._name_ == "CONST":
			return _("固定値")
		elif self._name_ == "EDITABLE":
			return _("編集可能")
		elif self._name_ == "SELECT":
			return _("選択")
		elif self._name_ == "ENCORDED":
			return _("エンコード済固定値")
		else:
			raise ValueError(self._name_)


class ContentType(IntEnum):
	JSON = 0
	FORM = 1

	@property
	def header_value(self):
		"""The Content-Type header value of the Enum member."""
		if self._name_ == "JSON":
			return "application/json; charset=utf-8"
		else:
			return "application/x-www-form-urlencoded"

class HeaderFieldTypeEnumMeta(EnumMeta):
	def __getitem__(self, value):
		if value == _("固定値"):
			return super().__getitem__("CONST")
		elif value == _("編集可能"):
			return super().__getitem__("EDITABLE")
		elif value == _("選択"):
			return super().__getitem__("SELECT")
		elif value == _("削除"):
			return super().__getitem__("REMOVE")
		else:
			return super().__getitem__(value)

@unique
class HeaderFieldType(IntEnum, metaclass=HeaderFieldTypeEnumMeta):
	CONST = 0
	EDITABLE = 1
	SELECT = 2
	REMOVE = 3

	@property
	def view_name(self):
		"""The name of the Enum member."""
		if self._name_ == "CONST":
			return _("固定値")
		elif self._name_ == "EDITABLE":
			return _("編集可能")
		elif self._name_ == "SELECT":
			return _("選択")
		elif self._name_ == "REMOVE":
			return _("削除")
		else:
			raise ValueError(self._name_)

class Method(IntEnum):
	GET = 0
	POST = 1
	PUT = 2
	PATCH = 3
	DELETE = 4
	HEADER = 5

class UriFieldTypeEnumMeta(EnumMeta):
	def __getitem__(self, value):
		if value == _("編集可能"):
			return super().__getitem__("EDITABLE")
		else:
			return super().__getitem__(value)

@unique
class UriFieldType(IntEnum, metaclass=UriFieldTypeEnumMeta):
	EDITABLE = 0
	SELECT = 1

	@property
	def view_name(self):
		"""The name of the Enum member."""
		if self._name_ == "EDITABLE":
			return _("編集可能")
		elif self._name_ == "SELECT":
			return _("選択")
		else:
			raise ValueError(self._name_)