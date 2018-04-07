# coding=utf-8
# -*- coding: utf-8 -*-
import colander


class LogUrl(colander.MappingSchema):
    from_ = colander.SchemaNode(
        name='from',
        typ=colander.Float(),
        validator=colander.Range(min=0),
        missing=colander.drop,
        description=u'Начало периода выборки логов'
    )

    to_ = colander.SchemaNode(
        name='to',
        typ=colander.Float(),
        validator=colander.Range(min=0),
        missing=colander.drop,
        description=u'Конец периода выборки логов'
    )

    page = colander.SchemaNode(
        name='page',
        typ=colander.Int(),
        validator=colander.Range(min=0),
        missing=colander.drop,
        description=u'Номер страницы в выборке'
    )

    items = colander.SchemaNode(
        name='items',
        typ=colander.Int(),
        validator=colander.Range(min=0),
        missing=colander.drop,
        description=u'Количество элементов в выборке'
    )