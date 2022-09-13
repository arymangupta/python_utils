# -*- coding: utf-8 -*-
# Generated by the protocol buffer compiler.  DO NOT EDIT!
# source: IAE_Configs.proto

import sys
_b=sys.version_info[0]<3 and (lambda x:x) or (lambda x:x.encode('latin1'))
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from google.protobuf import reflection as _reflection
from google.protobuf import symbol_database as _symbol_database
# @@protoc_insertion_point(imports)

_sym_db = _symbol_database.Default()




DESCRIPTOR = _descriptor.FileDescriptor(
  name='IAE_Configs.proto',
  package='IaeConfig',
  syntax='proto3',
  serialized_options=_b('\n\024com.virsec.iaeconfigB\tIaeConfig'),
  serialized_pb=_b('\n\x11IAE_Configs.proto\x12\tIaeConfig\"\x1e\n\x0eIAE_PB_RFI_MAP\x12\x0c\n\x04urls\x18\x01 \x03(\t\",\n\x0eIAE_PB_LFI_MAP\x12\x0c\n\x04\x64irs\x18\x01 \x03(\t\x12\x0c\n\x04\x65xts\x18\x02 \x03(\t\"\xa5\x0c\n\x14IAE_PB_CONFIG_COMMON\x12\r\n\x05\x61siId\x18\x01 \x01(\x05\x12\x13\n\x0bnamespaceId\x18\x02 \x01(\x04\x12\x17\n\x0f\x61ppCollectiveId\x18\x03 \x01(\x03\x12\x0f\n\x07vulMask\x18\x04 \x01(\x03\x12\x16\n\x0eprotectVulMask\x18\x05 \x01(\x03\x12\x19\n\x11runningMapVersion\x18\x06 \x01(\x05\x12\x42\n\rreflectiveXSS\x18\x07 \x01(\x0e\x32+.IaeConfig.IAE_PB_CONFIG_COMMON.ProtectMode\x12\x39\n\x04SQLi\x18\x08 \x01(\x0e\x32+.IaeConfig.IAE_PB_CONFIG_COMMON.ProtectMode\x12\x43\n\x0einsiderProtect\x18\t \x01(\x0e\x32+.IaeConfig.IAE_PB_CONFIG_COMMON.ProtectMode\x12\x39\n\x04\x43SRF\x18\n \x01(\x0e\x32+.IaeConfig.IAE_PB_CONFIG_COMMON.ProtectMode\x12>\n\turlSQLLog\x18\x0b \x01(\x0e\x32+.IaeConfig.IAE_PB_CONFIG_COMMON.ProtectMode\x12>\n\tstoredXSS\x18\x0c \x01(\x0e\x32+.IaeConfig.IAE_PB_CONFIG_COMMON.ProtectMode\x12:\n\x05\x43RLFi\x18\r \x01(\x0e\x32+.IaeConfig.IAE_PB_CONFIG_COMMON.ProtectMode\x12\x39\n\x04\x43MDi\x18\x0e \x01(\x0e\x32+.IaeConfig.IAE_PB_CONFIG_COMMON.ProtectMode\x12\x43\n\x0epathTraversali\x18\x0f \x01(\x0e\x32+.IaeConfig.IAE_PB_CONFIG_COMMON.ProtectMode\x12\x41\n\x0c\x63lassLoadLog\x18\x10 \x01(\x0e\x32+.IaeConfig.IAE_PB_CONFIG_COMMON.ProtectMode\x12\x43\n\x0esoftwareExcLog\x18\x11 \x01(\x0e\x32+.IaeConfig.IAE_PB_CONFIG_COMMON.ProtectMode\x12\x38\n\x03LFI\x18\x12 \x01(\x0e\x32+.IaeConfig.IAE_PB_CONFIG_COMMON.ProtectMode\x12\x38\n\x03RFI\x18\x13 \x01(\x0e\x32+.IaeConfig.IAE_PB_CONFIG_COMMON.ProtectMode\x12;\n\x06\x64omXSS\x18\x14 \x01(\x0e\x32+.IaeConfig.IAE_PB_CONFIG_COMMON.ProtectMode\x12\x43\n\x0eprotocolAttack\x18\x15 \x01(\x0e\x32+.IaeConfig.IAE_PB_CONFIG_COMMON.ProtectMode\x12H\n\x13protocolEnforcement\x18\x16 \x01(\x0e\x32+.IaeConfig.IAE_PB_CONFIG_COMMON.ProtectMode\x12\x41\n\x0cXMLInjection\x18\x17 \x01(\x0e\x32+.IaeConfig.IAE_PB_CONFIG_COMMON.ProtectMode\x12\x46\n\x11methodEnforcement\x18\x18 \x01(\x0e\x32+.IaeConfig.IAE_PB_CONFIG_COMMON.ProtectMode\x12;\n\x06\x63ustom\x18\x19 \x01(\x0e\x32+.IaeConfig.IAE_PB_CONFIG_COMMON.ProtectMode\x12\x37\n\x02\x42\x45\x18\x1a \x01(\x0e\x32+.IaeConfig.IAE_PB_CONFIG_COMMON.ProtectMode\x12@\n\x0bprotectMode\x18\x1b \x01(\x0e\x32+.IaeConfig.IAE_PB_CONFIG_COMMON.ProtectMode\x12\x14\n\x0cwebProfileId\x18\x1c \x01(\t\"0\n\x0bProtectMode\x12\x08\n\x04NONE\x10\x00\x12\n\n\x06\x44\x45TECT\x10\x01\x12\x0b\n\x07PROTECT\x10\x02\"\xa9\x01\n\x1bIAE_PB_APPCOLLECTIVE_CONFIG\x12\x0f\n\x07\x61ppName\x18\x01 \x01(\t\x12\x12\n\nappContext\x18\x02 \x01(\t\x12\x0f\n\x07\x61ppPath\x18\x03 \x03(\t\x12)\n\x06RfiMap\x18\x04 \x01(\x0b\x32\x19.IaeConfig.IAE_PB_RFI_MAP\x12)\n\x06LfiMap\x18\x05 \x01(\x0b\x32\x19.IaeConfig.IAE_PB_LFI_MAP\"\xe2\x01\n\x1bIAE_PB_WEBCOLLECTIVE_CONFIG\x12\x1b\n\x13\x61pplicationHostName\x18\x01 \x03(\t\x12\x15\n\rwebServerName\x18\x02 \x01(\t\x12\x15\n\rwebServerType\x18\x03 \x01(\t\x12\x18\n\x10webServerVersion\x18\x04 \x01(\t\x12\x14\n\x0cwebServerCfg\x18\x05 \x01(\t\x12\x18\n\x10webServerBinPath\x18\x07 \x01(\t\x12\x18\n\x10webServerLogPath\x18\x08 \x01(\t\x12\x14\n\x0cwebServerCMD\x18\t \x01(\t\"\xda\x02\n\rIAE_PB_CONFIG\x12/\n\x06\x63ommon\x18\x01 \x01(\x0b\x32\x1f.IaeConfig.IAE_PB_CONFIG_COMMON\x12\x37\n\nconfigType\x18\x02 \x01(\x0e\x32#.IaeConfig.IAE_PB_CONFIG.ConfigType\x12\x45\n\x13\x61ppCollectiveConfig\x18\n \x01(\x0b\x32&.IaeConfig.IAE_PB_APPCOLLECTIVE_CONFIGH\x00\x12\x45\n\x13webCollectiveConfig\x18\x0b \x01(\x0b\x32&.IaeConfig.IAE_PB_WEBCOLLECTIVE_CONFIGH\x00\">\n\nConfigType\x12\x08\n\x04NONE\x10\x00\x12\x12\n\x0e\x41PP_COLLECTIVE\x10\x01\x12\x12\n\x0eWEB_COLLECTIVE\x10\x02\x42\x11\n\x0fmessage_elementB!\n\x14\x63om.virsec.iaeconfigB\tIaeConfigb\x06proto3')
)



_IAE_PB_CONFIG_COMMON_PROTECTMODE = _descriptor.EnumDescriptor(
  name='ProtectMode',
  full_name='IaeConfig.IAE_PB_CONFIG_COMMON.ProtectMode',
  filename=None,
  file=DESCRIPTOR,
  values=[
    _descriptor.EnumValueDescriptor(
      name='NONE', index=0, number=0,
      serialized_options=None,
      type=None),
    _descriptor.EnumValueDescriptor(
      name='DETECT', index=1, number=1,
      serialized_options=None,
      type=None),
    _descriptor.EnumValueDescriptor(
      name='PROTECT', index=2, number=2,
      serialized_options=None,
      type=None),
  ],
  containing_type=None,
  serialized_options=None,
  serialized_start=1636,
  serialized_end=1684,
)
_sym_db.RegisterEnumDescriptor(_IAE_PB_CONFIG_COMMON_PROTECTMODE)

_IAE_PB_CONFIG_CONFIGTYPE = _descriptor.EnumDescriptor(
  name='ConfigType',
  full_name='IaeConfig.IAE_PB_CONFIG.ConfigType',
  filename=None,
  file=DESCRIPTOR,
  values=[
    _descriptor.EnumValueDescriptor(
      name='NONE', index=0, number=0,
      serialized_options=None,
      type=None),
    _descriptor.EnumValueDescriptor(
      name='APP_COLLECTIVE', index=1, number=1,
      serialized_options=None,
      type=None),
    _descriptor.EnumValueDescriptor(
      name='WEB_COLLECTIVE', index=2, number=2,
      serialized_options=None,
      type=None),
  ],
  containing_type=None,
  serialized_options=None,
  serialized_start=2353,
  serialized_end=2415,
)
_sym_db.RegisterEnumDescriptor(_IAE_PB_CONFIG_CONFIGTYPE)


_IAE_PB_RFI_MAP = _descriptor.Descriptor(
  name='IAE_PB_RFI_MAP',
  full_name='IaeConfig.IAE_PB_RFI_MAP',
  filename=None,
  file=DESCRIPTOR,
  containing_type=None,
  fields=[
    _descriptor.FieldDescriptor(
      name='urls', full_name='IaeConfig.IAE_PB_RFI_MAP.urls', index=0,
      number=1, type=9, cpp_type=9, label=3,
      has_default_value=False, default_value=[],
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      serialized_options=None, file=DESCRIPTOR),
  ],
  extensions=[
  ],
  nested_types=[],
  enum_types=[
  ],
  serialized_options=None,
  is_extendable=False,
  syntax='proto3',
  extension_ranges=[],
  oneofs=[
  ],
  serialized_start=32,
  serialized_end=62,
)


_IAE_PB_LFI_MAP = _descriptor.Descriptor(
  name='IAE_PB_LFI_MAP',
  full_name='IaeConfig.IAE_PB_LFI_MAP',
  filename=None,
  file=DESCRIPTOR,
  containing_type=None,
  fields=[
    _descriptor.FieldDescriptor(
      name='dirs', full_name='IaeConfig.IAE_PB_LFI_MAP.dirs', index=0,
      number=1, type=9, cpp_type=9, label=3,
      has_default_value=False, default_value=[],
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      serialized_options=None, file=DESCRIPTOR),
    _descriptor.FieldDescriptor(
      name='exts', full_name='IaeConfig.IAE_PB_LFI_MAP.exts', index=1,
      number=2, type=9, cpp_type=9, label=3,
      has_default_value=False, default_value=[],
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      serialized_options=None, file=DESCRIPTOR),
  ],
  extensions=[
  ],
  nested_types=[],
  enum_types=[
  ],
  serialized_options=None,
  is_extendable=False,
  syntax='proto3',
  extension_ranges=[],
  oneofs=[
  ],
  serialized_start=64,
  serialized_end=108,
)


_IAE_PB_CONFIG_COMMON = _descriptor.Descriptor(
  name='IAE_PB_CONFIG_COMMON',
  full_name='IaeConfig.IAE_PB_CONFIG_COMMON',
  filename=None,
  file=DESCRIPTOR,
  containing_type=None,
  fields=[
    _descriptor.FieldDescriptor(
      name='asiId', full_name='IaeConfig.IAE_PB_CONFIG_COMMON.asiId', index=0,
      number=1, type=5, cpp_type=1, label=1,
      has_default_value=False, default_value=0,
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      serialized_options=None, file=DESCRIPTOR),
    _descriptor.FieldDescriptor(
      name='namespaceId', full_name='IaeConfig.IAE_PB_CONFIG_COMMON.namespaceId', index=1,
      number=2, type=4, cpp_type=4, label=1,
      has_default_value=False, default_value=0,
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      serialized_options=None, file=DESCRIPTOR),
    _descriptor.FieldDescriptor(
      name='appCollectiveId', full_name='IaeConfig.IAE_PB_CONFIG_COMMON.appCollectiveId', index=2,
      number=3, type=3, cpp_type=2, label=1,
      has_default_value=False, default_value=0,
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      serialized_options=None, file=DESCRIPTOR),
    _descriptor.FieldDescriptor(
      name='vulMask', full_name='IaeConfig.IAE_PB_CONFIG_COMMON.vulMask', index=3,
      number=4, type=3, cpp_type=2, label=1,
      has_default_value=False, default_value=0,
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      serialized_options=None, file=DESCRIPTOR),
    _descriptor.FieldDescriptor(
      name='protectVulMask', full_name='IaeConfig.IAE_PB_CONFIG_COMMON.protectVulMask', index=4,
      number=5, type=3, cpp_type=2, label=1,
      has_default_value=False, default_value=0,
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      serialized_options=None, file=DESCRIPTOR),
    _descriptor.FieldDescriptor(
      name='runningMapVersion', full_name='IaeConfig.IAE_PB_CONFIG_COMMON.runningMapVersion', index=5,
      number=6, type=5, cpp_type=1, label=1,
      has_default_value=False, default_value=0,
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      serialized_options=None, file=DESCRIPTOR),
    _descriptor.FieldDescriptor(
      name='reflectiveXSS', full_name='IaeConfig.IAE_PB_CONFIG_COMMON.reflectiveXSS', index=6,
      number=7, type=14, cpp_type=8, label=1,
      has_default_value=False, default_value=0,
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      serialized_options=None, file=DESCRIPTOR),
    _descriptor.FieldDescriptor(
      name='SQLi', full_name='IaeConfig.IAE_PB_CONFIG_COMMON.SQLi', index=7,
      number=8, type=14, cpp_type=8, label=1,
      has_default_value=False, default_value=0,
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      serialized_options=None, file=DESCRIPTOR),
    _descriptor.FieldDescriptor(
      name='insiderProtect', full_name='IaeConfig.IAE_PB_CONFIG_COMMON.insiderProtect', index=8,
      number=9, type=14, cpp_type=8, label=1,
      has_default_value=False, default_value=0,
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      serialized_options=None, file=DESCRIPTOR),
    _descriptor.FieldDescriptor(
      name='CSRF', full_name='IaeConfig.IAE_PB_CONFIG_COMMON.CSRF', index=9,
      number=10, type=14, cpp_type=8, label=1,
      has_default_value=False, default_value=0,
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      serialized_options=None, file=DESCRIPTOR),
    _descriptor.FieldDescriptor(
      name='urlSQLLog', full_name='IaeConfig.IAE_PB_CONFIG_COMMON.urlSQLLog', index=10,
      number=11, type=14, cpp_type=8, label=1,
      has_default_value=False, default_value=0,
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      serialized_options=None, file=DESCRIPTOR),
    _descriptor.FieldDescriptor(
      name='storedXSS', full_name='IaeConfig.IAE_PB_CONFIG_COMMON.storedXSS', index=11,
      number=12, type=14, cpp_type=8, label=1,
      has_default_value=False, default_value=0,
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      serialized_options=None, file=DESCRIPTOR),
    _descriptor.FieldDescriptor(
      name='CRLFi', full_name='IaeConfig.IAE_PB_CONFIG_COMMON.CRLFi', index=12,
      number=13, type=14, cpp_type=8, label=1,
      has_default_value=False, default_value=0,
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      serialized_options=None, file=DESCRIPTOR),
    _descriptor.FieldDescriptor(
      name='CMDi', full_name='IaeConfig.IAE_PB_CONFIG_COMMON.CMDi', index=13,
      number=14, type=14, cpp_type=8, label=1,
      has_default_value=False, default_value=0,
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      serialized_options=None, file=DESCRIPTOR),
    _descriptor.FieldDescriptor(
      name='pathTraversali', full_name='IaeConfig.IAE_PB_CONFIG_COMMON.pathTraversali', index=14,
      number=15, type=14, cpp_type=8, label=1,
      has_default_value=False, default_value=0,
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      serialized_options=None, file=DESCRIPTOR),
    _descriptor.FieldDescriptor(
      name='classLoadLog', full_name='IaeConfig.IAE_PB_CONFIG_COMMON.classLoadLog', index=15,
      number=16, type=14, cpp_type=8, label=1,
      has_default_value=False, default_value=0,
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      serialized_options=None, file=DESCRIPTOR),
    _descriptor.FieldDescriptor(
      name='softwareExcLog', full_name='IaeConfig.IAE_PB_CONFIG_COMMON.softwareExcLog', index=16,
      number=17, type=14, cpp_type=8, label=1,
      has_default_value=False, default_value=0,
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      serialized_options=None, file=DESCRIPTOR),
    _descriptor.FieldDescriptor(
      name='LFI', full_name='IaeConfig.IAE_PB_CONFIG_COMMON.LFI', index=17,
      number=18, type=14, cpp_type=8, label=1,
      has_default_value=False, default_value=0,
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      serialized_options=None, file=DESCRIPTOR),
    _descriptor.FieldDescriptor(
      name='RFI', full_name='IaeConfig.IAE_PB_CONFIG_COMMON.RFI', index=18,
      number=19, type=14, cpp_type=8, label=1,
      has_default_value=False, default_value=0,
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      serialized_options=None, file=DESCRIPTOR),
    _descriptor.FieldDescriptor(
      name='domXSS', full_name='IaeConfig.IAE_PB_CONFIG_COMMON.domXSS', index=19,
      number=20, type=14, cpp_type=8, label=1,
      has_default_value=False, default_value=0,
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      serialized_options=None, file=DESCRIPTOR),
    _descriptor.FieldDescriptor(
      name='protocolAttack', full_name='IaeConfig.IAE_PB_CONFIG_COMMON.protocolAttack', index=20,
      number=21, type=14, cpp_type=8, label=1,
      has_default_value=False, default_value=0,
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      serialized_options=None, file=DESCRIPTOR),
    _descriptor.FieldDescriptor(
      name='protocolEnforcement', full_name='IaeConfig.IAE_PB_CONFIG_COMMON.protocolEnforcement', index=21,
      number=22, type=14, cpp_type=8, label=1,
      has_default_value=False, default_value=0,
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      serialized_options=None, file=DESCRIPTOR),
    _descriptor.FieldDescriptor(
      name='XMLInjection', full_name='IaeConfig.IAE_PB_CONFIG_COMMON.XMLInjection', index=22,
      number=23, type=14, cpp_type=8, label=1,
      has_default_value=False, default_value=0,
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      serialized_options=None, file=DESCRIPTOR),
    _descriptor.FieldDescriptor(
      name='methodEnforcement', full_name='IaeConfig.IAE_PB_CONFIG_COMMON.methodEnforcement', index=23,
      number=24, type=14, cpp_type=8, label=1,
      has_default_value=False, default_value=0,
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      serialized_options=None, file=DESCRIPTOR),
    _descriptor.FieldDescriptor(
      name='custom', full_name='IaeConfig.IAE_PB_CONFIG_COMMON.custom', index=24,
      number=25, type=14, cpp_type=8, label=1,
      has_default_value=False, default_value=0,
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      serialized_options=None, file=DESCRIPTOR),
    _descriptor.FieldDescriptor(
      name='BE', full_name='IaeConfig.IAE_PB_CONFIG_COMMON.BE', index=25,
      number=26, type=14, cpp_type=8, label=1,
      has_default_value=False, default_value=0,
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      serialized_options=None, file=DESCRIPTOR),
    _descriptor.FieldDescriptor(
      name='protectMode', full_name='IaeConfig.IAE_PB_CONFIG_COMMON.protectMode', index=26,
      number=27, type=14, cpp_type=8, label=1,
      has_default_value=False, default_value=0,
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      serialized_options=None, file=DESCRIPTOR),
    _descriptor.FieldDescriptor(
      name='webProfileId', full_name='IaeConfig.IAE_PB_CONFIG_COMMON.webProfileId', index=27,
      number=28, type=9, cpp_type=9, label=1,
      has_default_value=False, default_value=_b("").decode('utf-8'),
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      serialized_options=None, file=DESCRIPTOR),
  ],
  extensions=[
  ],
  nested_types=[],
  enum_types=[
    _IAE_PB_CONFIG_COMMON_PROTECTMODE,
  ],
  serialized_options=None,
  is_extendable=False,
  syntax='proto3',
  extension_ranges=[],
  oneofs=[
  ],
  serialized_start=111,
  serialized_end=1684,
)


_IAE_PB_APPCOLLECTIVE_CONFIG = _descriptor.Descriptor(
  name='IAE_PB_APPCOLLECTIVE_CONFIG',
  full_name='IaeConfig.IAE_PB_APPCOLLECTIVE_CONFIG',
  filename=None,
  file=DESCRIPTOR,
  containing_type=None,
  fields=[
    _descriptor.FieldDescriptor(
      name='appName', full_name='IaeConfig.IAE_PB_APPCOLLECTIVE_CONFIG.appName', index=0,
      number=1, type=9, cpp_type=9, label=1,
      has_default_value=False, default_value=_b("").decode('utf-8'),
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      serialized_options=None, file=DESCRIPTOR),
    _descriptor.FieldDescriptor(
      name='appContext', full_name='IaeConfig.IAE_PB_APPCOLLECTIVE_CONFIG.appContext', index=1,
      number=2, type=9, cpp_type=9, label=1,
      has_default_value=False, default_value=_b("").decode('utf-8'),
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      serialized_options=None, file=DESCRIPTOR),
    _descriptor.FieldDescriptor(
      name='appPath', full_name='IaeConfig.IAE_PB_APPCOLLECTIVE_CONFIG.appPath', index=2,
      number=3, type=9, cpp_type=9, label=3,
      has_default_value=False, default_value=[],
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      serialized_options=None, file=DESCRIPTOR),
    _descriptor.FieldDescriptor(
      name='RfiMap', full_name='IaeConfig.IAE_PB_APPCOLLECTIVE_CONFIG.RfiMap', index=3,
      number=4, type=11, cpp_type=10, label=1,
      has_default_value=False, default_value=None,
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      serialized_options=None, file=DESCRIPTOR),
    _descriptor.FieldDescriptor(
      name='LfiMap', full_name='IaeConfig.IAE_PB_APPCOLLECTIVE_CONFIG.LfiMap', index=4,
      number=5, type=11, cpp_type=10, label=1,
      has_default_value=False, default_value=None,
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      serialized_options=None, file=DESCRIPTOR),
  ],
  extensions=[
  ],
  nested_types=[],
  enum_types=[
  ],
  serialized_options=None,
  is_extendable=False,
  syntax='proto3',
  extension_ranges=[],
  oneofs=[
  ],
  serialized_start=1687,
  serialized_end=1856,
)


_IAE_PB_WEBCOLLECTIVE_CONFIG = _descriptor.Descriptor(
  name='IAE_PB_WEBCOLLECTIVE_CONFIG',
  full_name='IaeConfig.IAE_PB_WEBCOLLECTIVE_CONFIG',
  filename=None,
  file=DESCRIPTOR,
  containing_type=None,
  fields=[
    _descriptor.FieldDescriptor(
      name='applicationHostName', full_name='IaeConfig.IAE_PB_WEBCOLLECTIVE_CONFIG.applicationHostName', index=0,
      number=1, type=9, cpp_type=9, label=3,
      has_default_value=False, default_value=[],
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      serialized_options=None, file=DESCRIPTOR),
    _descriptor.FieldDescriptor(
      name='webServerName', full_name='IaeConfig.IAE_PB_WEBCOLLECTIVE_CONFIG.webServerName', index=1,
      number=2, type=9, cpp_type=9, label=1,
      has_default_value=False, default_value=_b("").decode('utf-8'),
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      serialized_options=None, file=DESCRIPTOR),
    _descriptor.FieldDescriptor(
      name='webServerType', full_name='IaeConfig.IAE_PB_WEBCOLLECTIVE_CONFIG.webServerType', index=2,
      number=3, type=9, cpp_type=9, label=1,
      has_default_value=False, default_value=_b("").decode('utf-8'),
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      serialized_options=None, file=DESCRIPTOR),
    _descriptor.FieldDescriptor(
      name='webServerVersion', full_name='IaeConfig.IAE_PB_WEBCOLLECTIVE_CONFIG.webServerVersion', index=3,
      number=4, type=9, cpp_type=9, label=1,
      has_default_value=False, default_value=_b("").decode('utf-8'),
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      serialized_options=None, file=DESCRIPTOR),
    _descriptor.FieldDescriptor(
      name='webServerCfg', full_name='IaeConfig.IAE_PB_WEBCOLLECTIVE_CONFIG.webServerCfg', index=4,
      number=5, type=9, cpp_type=9, label=1,
      has_default_value=False, default_value=_b("").decode('utf-8'),
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      serialized_options=None, file=DESCRIPTOR),
    _descriptor.FieldDescriptor(
      name='webServerBinPath', full_name='IaeConfig.IAE_PB_WEBCOLLECTIVE_CONFIG.webServerBinPath', index=5,
      number=7, type=9, cpp_type=9, label=1,
      has_default_value=False, default_value=_b("").decode('utf-8'),
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      serialized_options=None, file=DESCRIPTOR),
    _descriptor.FieldDescriptor(
      name='webServerLogPath', full_name='IaeConfig.IAE_PB_WEBCOLLECTIVE_CONFIG.webServerLogPath', index=6,
      number=8, type=9, cpp_type=9, label=1,
      has_default_value=False, default_value=_b("").decode('utf-8'),
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      serialized_options=None, file=DESCRIPTOR),
    _descriptor.FieldDescriptor(
      name='webServerCMD', full_name='IaeConfig.IAE_PB_WEBCOLLECTIVE_CONFIG.webServerCMD', index=7,
      number=9, type=9, cpp_type=9, label=1,
      has_default_value=False, default_value=_b("").decode('utf-8'),
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      serialized_options=None, file=DESCRIPTOR),
  ],
  extensions=[
  ],
  nested_types=[],
  enum_types=[
  ],
  serialized_options=None,
  is_extendable=False,
  syntax='proto3',
  extension_ranges=[],
  oneofs=[
  ],
  serialized_start=1859,
  serialized_end=2085,
)


_IAE_PB_CONFIG = _descriptor.Descriptor(
  name='IAE_PB_CONFIG',
  full_name='IaeConfig.IAE_PB_CONFIG',
  filename=None,
  file=DESCRIPTOR,
  containing_type=None,
  fields=[
    _descriptor.FieldDescriptor(
      name='common', full_name='IaeConfig.IAE_PB_CONFIG.common', index=0,
      number=1, type=11, cpp_type=10, label=1,
      has_default_value=False, default_value=None,
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      serialized_options=None, file=DESCRIPTOR),
    _descriptor.FieldDescriptor(
      name='configType', full_name='IaeConfig.IAE_PB_CONFIG.configType', index=1,
      number=2, type=14, cpp_type=8, label=1,
      has_default_value=False, default_value=0,
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      serialized_options=None, file=DESCRIPTOR),
    _descriptor.FieldDescriptor(
      name='appCollectiveConfig', full_name='IaeConfig.IAE_PB_CONFIG.appCollectiveConfig', index=2,
      number=10, type=11, cpp_type=10, label=1,
      has_default_value=False, default_value=None,
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      serialized_options=None, file=DESCRIPTOR),
    _descriptor.FieldDescriptor(
      name='webCollectiveConfig', full_name='IaeConfig.IAE_PB_CONFIG.webCollectiveConfig', index=3,
      number=11, type=11, cpp_type=10, label=1,
      has_default_value=False, default_value=None,
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      serialized_options=None, file=DESCRIPTOR),
  ],
  extensions=[
  ],
  nested_types=[],
  enum_types=[
    _IAE_PB_CONFIG_CONFIGTYPE,
  ],
  serialized_options=None,
  is_extendable=False,
  syntax='proto3',
  extension_ranges=[],
  oneofs=[
    _descriptor.OneofDescriptor(
      name='message_element', full_name='IaeConfig.IAE_PB_CONFIG.message_element',
      index=0, containing_type=None, fields=[]),
  ],
  serialized_start=2088,
  serialized_end=2434,
)

_IAE_PB_CONFIG_COMMON.fields_by_name['reflectiveXSS'].enum_type = _IAE_PB_CONFIG_COMMON_PROTECTMODE
_IAE_PB_CONFIG_COMMON.fields_by_name['SQLi'].enum_type = _IAE_PB_CONFIG_COMMON_PROTECTMODE
_IAE_PB_CONFIG_COMMON.fields_by_name['insiderProtect'].enum_type = _IAE_PB_CONFIG_COMMON_PROTECTMODE
_IAE_PB_CONFIG_COMMON.fields_by_name['CSRF'].enum_type = _IAE_PB_CONFIG_COMMON_PROTECTMODE
_IAE_PB_CONFIG_COMMON.fields_by_name['urlSQLLog'].enum_type = _IAE_PB_CONFIG_COMMON_PROTECTMODE
_IAE_PB_CONFIG_COMMON.fields_by_name['storedXSS'].enum_type = _IAE_PB_CONFIG_COMMON_PROTECTMODE
_IAE_PB_CONFIG_COMMON.fields_by_name['CRLFi'].enum_type = _IAE_PB_CONFIG_COMMON_PROTECTMODE
_IAE_PB_CONFIG_COMMON.fields_by_name['CMDi'].enum_type = _IAE_PB_CONFIG_COMMON_PROTECTMODE
_IAE_PB_CONFIG_COMMON.fields_by_name['pathTraversali'].enum_type = _IAE_PB_CONFIG_COMMON_PROTECTMODE
_IAE_PB_CONFIG_COMMON.fields_by_name['classLoadLog'].enum_type = _IAE_PB_CONFIG_COMMON_PROTECTMODE
_IAE_PB_CONFIG_COMMON.fields_by_name['softwareExcLog'].enum_type = _IAE_PB_CONFIG_COMMON_PROTECTMODE
_IAE_PB_CONFIG_COMMON.fields_by_name['LFI'].enum_type = _IAE_PB_CONFIG_COMMON_PROTECTMODE
_IAE_PB_CONFIG_COMMON.fields_by_name['RFI'].enum_type = _IAE_PB_CONFIG_COMMON_PROTECTMODE
_IAE_PB_CONFIG_COMMON.fields_by_name['domXSS'].enum_type = _IAE_PB_CONFIG_COMMON_PROTECTMODE
_IAE_PB_CONFIG_COMMON.fields_by_name['protocolAttack'].enum_type = _IAE_PB_CONFIG_COMMON_PROTECTMODE
_IAE_PB_CONFIG_COMMON.fields_by_name['protocolEnforcement'].enum_type = _IAE_PB_CONFIG_COMMON_PROTECTMODE
_IAE_PB_CONFIG_COMMON.fields_by_name['XMLInjection'].enum_type = _IAE_PB_CONFIG_COMMON_PROTECTMODE
_IAE_PB_CONFIG_COMMON.fields_by_name['methodEnforcement'].enum_type = _IAE_PB_CONFIG_COMMON_PROTECTMODE
_IAE_PB_CONFIG_COMMON.fields_by_name['custom'].enum_type = _IAE_PB_CONFIG_COMMON_PROTECTMODE
_IAE_PB_CONFIG_COMMON.fields_by_name['BE'].enum_type = _IAE_PB_CONFIG_COMMON_PROTECTMODE
_IAE_PB_CONFIG_COMMON.fields_by_name['protectMode'].enum_type = _IAE_PB_CONFIG_COMMON_PROTECTMODE
_IAE_PB_CONFIG_COMMON_PROTECTMODE.containing_type = _IAE_PB_CONFIG_COMMON
_IAE_PB_APPCOLLECTIVE_CONFIG.fields_by_name['RfiMap'].message_type = _IAE_PB_RFI_MAP
_IAE_PB_APPCOLLECTIVE_CONFIG.fields_by_name['LfiMap'].message_type = _IAE_PB_LFI_MAP
_IAE_PB_CONFIG.fields_by_name['common'].message_type = _IAE_PB_CONFIG_COMMON
_IAE_PB_CONFIG.fields_by_name['configType'].enum_type = _IAE_PB_CONFIG_CONFIGTYPE
_IAE_PB_CONFIG.fields_by_name['appCollectiveConfig'].message_type = _IAE_PB_APPCOLLECTIVE_CONFIG
_IAE_PB_CONFIG.fields_by_name['webCollectiveConfig'].message_type = _IAE_PB_WEBCOLLECTIVE_CONFIG
_IAE_PB_CONFIG_CONFIGTYPE.containing_type = _IAE_PB_CONFIG
_IAE_PB_CONFIG.oneofs_by_name['message_element'].fields.append(
  _IAE_PB_CONFIG.fields_by_name['appCollectiveConfig'])
_IAE_PB_CONFIG.fields_by_name['appCollectiveConfig'].containing_oneof = _IAE_PB_CONFIG.oneofs_by_name['message_element']
_IAE_PB_CONFIG.oneofs_by_name['message_element'].fields.append(
  _IAE_PB_CONFIG.fields_by_name['webCollectiveConfig'])
_IAE_PB_CONFIG.fields_by_name['webCollectiveConfig'].containing_oneof = _IAE_PB_CONFIG.oneofs_by_name['message_element']
DESCRIPTOR.message_types_by_name['IAE_PB_RFI_MAP'] = _IAE_PB_RFI_MAP
DESCRIPTOR.message_types_by_name['IAE_PB_LFI_MAP'] = _IAE_PB_LFI_MAP
DESCRIPTOR.message_types_by_name['IAE_PB_CONFIG_COMMON'] = _IAE_PB_CONFIG_COMMON
DESCRIPTOR.message_types_by_name['IAE_PB_APPCOLLECTIVE_CONFIG'] = _IAE_PB_APPCOLLECTIVE_CONFIG
DESCRIPTOR.message_types_by_name['IAE_PB_WEBCOLLECTIVE_CONFIG'] = _IAE_PB_WEBCOLLECTIVE_CONFIG
DESCRIPTOR.message_types_by_name['IAE_PB_CONFIG'] = _IAE_PB_CONFIG
_sym_db.RegisterFileDescriptor(DESCRIPTOR)

IAE_PB_RFI_MAP = _reflection.GeneratedProtocolMessageType('IAE_PB_RFI_MAP', (_message.Message,), {
  'DESCRIPTOR' : _IAE_PB_RFI_MAP,
  '__module__' : 'IAE_Configs_pb2'
  # @@protoc_insertion_point(class_scope:IaeConfig.IAE_PB_RFI_MAP)
  })
_sym_db.RegisterMessage(IAE_PB_RFI_MAP)

IAE_PB_LFI_MAP = _reflection.GeneratedProtocolMessageType('IAE_PB_LFI_MAP', (_message.Message,), {
  'DESCRIPTOR' : _IAE_PB_LFI_MAP,
  '__module__' : 'IAE_Configs_pb2'
  # @@protoc_insertion_point(class_scope:IaeConfig.IAE_PB_LFI_MAP)
  })
_sym_db.RegisterMessage(IAE_PB_LFI_MAP)

IAE_PB_CONFIG_COMMON = _reflection.GeneratedProtocolMessageType('IAE_PB_CONFIG_COMMON', (_message.Message,), {
  'DESCRIPTOR' : _IAE_PB_CONFIG_COMMON,
  '__module__' : 'IAE_Configs_pb2'
  # @@protoc_insertion_point(class_scope:IaeConfig.IAE_PB_CONFIG_COMMON)
  })
_sym_db.RegisterMessage(IAE_PB_CONFIG_COMMON)

IAE_PB_APPCOLLECTIVE_CONFIG = _reflection.GeneratedProtocolMessageType('IAE_PB_APPCOLLECTIVE_CONFIG', (_message.Message,), {
  'DESCRIPTOR' : _IAE_PB_APPCOLLECTIVE_CONFIG,
  '__module__' : 'IAE_Configs_pb2'
  # @@protoc_insertion_point(class_scope:IaeConfig.IAE_PB_APPCOLLECTIVE_CONFIG)
  })
_sym_db.RegisterMessage(IAE_PB_APPCOLLECTIVE_CONFIG)

IAE_PB_WEBCOLLECTIVE_CONFIG = _reflection.GeneratedProtocolMessageType('IAE_PB_WEBCOLLECTIVE_CONFIG', (_message.Message,), {
  'DESCRIPTOR' : _IAE_PB_WEBCOLLECTIVE_CONFIG,
  '__module__' : 'IAE_Configs_pb2'
  # @@protoc_insertion_point(class_scope:IaeConfig.IAE_PB_WEBCOLLECTIVE_CONFIG)
  })
_sym_db.RegisterMessage(IAE_PB_WEBCOLLECTIVE_CONFIG)

IAE_PB_CONFIG = _reflection.GeneratedProtocolMessageType('IAE_PB_CONFIG', (_message.Message,), {
  'DESCRIPTOR' : _IAE_PB_CONFIG,
  '__module__' : 'IAE_Configs_pb2'
  # @@protoc_insertion_point(class_scope:IaeConfig.IAE_PB_CONFIG)
  })
_sym_db.RegisterMessage(IAE_PB_CONFIG)


DESCRIPTOR._options = None
# @@protoc_insertion_point(module_scope)