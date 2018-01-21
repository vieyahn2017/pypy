# -*- coding:utf-8 -*-
# --------------------
# Author:		Yh
# Description:
# --------------------
from wtforms import FileField,TextAreaField
from wtforms.validators import *
from wtforms_tornado import Form
import re


class UploadForm(Form):
    filename = FileField(u'选择文件')#, [validators.regexp(u'^[^/\\]\.jpg$')])
    #description  = TextAreaField(u'Image Description')

    def validate_image(form, field):
        if field.data:
            field.data = re.sub(r'[^a-z0-9_.-]', '_', field.data)


class UploadForm3(Form):
    image = FileField(u'Image File')#, [validators.regexp(u'^[^/\\]\.jpg$')])
    description  = TextAreaField(u'Image Description')

    def validate_image(form, field):
        if field.data:
            field.data = re.sub(r'[^a-z0-9_.-]', '_', field.data)


class UploadForm2(Form):
    file = FileField(u'选择文件')
