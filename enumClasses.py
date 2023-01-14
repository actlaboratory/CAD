# -*- coding: utf-8 -*-
# enum classes

import enum
from enum import IntEnum, EnumMeta, unique

class HeaderFieldTypeEnumMeta(EnumMeta):
	def __getitem__(self, value):
		if value == _("固定値"):
			return super().__getitem__("CONST")
		elif value == _("編集可能"):
			return super().__getitem__("EDITABLE")
		else:
			return super().__getitem__(value)

@unique
class HeaderFieldType(IntEnum, metaclass=HeaderFieldTypeEnumMeta):
	CONST = 0
	EDITABLE = 1
	SELECT = 2

	@property
	def view_name(self):
		"""The name of the Enum member."""
		if self._name_ == "CONST":
			return _("固定値")
		elif self._name_ == "EDITABLE":
			return _("編集可能")
		elif self._name_ == "SELECT":
			return _("選択")
		else:
			raise ValueError(self._name_)

class ContentType(IntEnum):
	JSON = 0
	FORM = 1


