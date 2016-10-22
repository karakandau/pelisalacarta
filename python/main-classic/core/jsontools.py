# -*- coding: utf-8 -*-
# ------------------------------------------------------------
# pelisalacarta 4
# Copyright 2015 tvalacarta@gmail.com
# http://blog.tvalacarta.info/plugin-xbmc/pelisalacarta/
#
# Distributed under the terms of GNU General Public License v3 (GPLv3)
# http://www.gnu.org/licenses/gpl-3.0.html
# ------------------------------------------------------------
# This file is part of pelisalacarta 4.
#
# pelisalacarta 4 is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# pelisalacarta 4 is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with pelisalacarta 4.  If not, see <http://www.gnu.org/licenses/>.
# --------------------------------------------------------------------------------
# json_tools - JSON load and parse functions with library detection
# --------------------------------------------------------------------------------

import traceback
import logger


def load_json(*args, **kwargs):

    try:
        logger.info("pelisalacarta.core.jsontools loads Probando simplejson en el directorio lib")
        from lib import simplejson as json
        if "object_hook" in kwargs:
            # return to_utf8(json.loads(*args, **kwargs))
            return json.loads(*args, **kwargs)
        else:
            # return to_utf8(json.loads(*args, object_hook=to_utf8))
            return json.loads(*args, object_hook=to_utf8)

    except ImportError:
        json = None
    except:
        logger.info(traceback.format_exc())

    # TODO comprobar si hace falta para plex
    try:
        logger.info("pelisalacarta.core.jsontools.load_json Probando JSON de Plex")
        json_data = JSON.ObjectFromString(*args, encoding="utf-8")
        logger.info("pelisalacarta.core.jsontools.load_json -> "+repr(json_data))
        return json_data
    except:
        logger.info(traceback.format_exc())

    logger.info("pelisalacarta.core.jsontools.load_json No se ha encontrado un parser de JSON valido")
    logger.info("pelisalacarta.core.jsontools.load_json -> (nada)")
    return {}


def dump_json(*args, **kwargs):

    try:
        logger.info("pelisalacarta.core.jsontools dumps Probando simplejson en el directorio lib")
        from lib import simplejson as json
        if kwargs:
            return json.dumps(*args, **kwargs)
        else:
            return json.dumps(*args, indent=4, skipkeys=True, sort_keys=True, ensure_ascii=False)
            # return json.dumps(*args, indent=4, sort_keys=True, ensure_ascii=False)
    except ImportError:
        json = None
    except:
        logger.info(traceback.format_exc())

    # TODO comprobar si hace falta para plex
    try:
        logger.info("pelisalacarta.core.jsontools.dump_json Probando JSON de Plex")
        json_data = JSON.StringFromObject(*args)   #, encoding="utf-8")
        logger.info("pelisalacarta.core.jsontools.dump_json -> "+repr(json_data))
        return json_data
    except:
        logger.info(traceback.format_exc())

    logger.info("pelisalacarta.core.jsontools.dump_json No se ha encontrado un parser de JSON valido")
    logger.info("pelisalacarta.core.jsontools.dump_json -> (nada)")
    return {}


def to_utf8(dct):

    if isinstance(dct, dict):
        return dict((to_utf8(key), to_utf8(value)) for key, value in dct.iteritems())
    elif isinstance(dct, list):
        return [to_utf8(element) for element in dct]
    elif isinstance(dct, unicode):
        return dct.encode('utf-8')
    else:
        return dct


def xmlTojson(path_xml):
    """
    Lee un fichero xml y retorna un diccionario json

    Parametros:
    path_xml (str) -- Ruta completa al archivo XML que se desea leer.

    Retorna:
    Si el argumento path_xml no señala a un archivo XML valido retorna un diccionario vacio.
    En caso cortrario retorna un diccionario construido a partir de los campos del archivo XML.

    """

    import os
    ret = {}
    try:
        if os.path.exists(path_xml):
            infile = open(path_xml, "rb")
            data = infile.read()
            infile.close()
            ret = Xml2Json(data).result
    except:
        import traceback
        logger.info("pelisalacarta.core.jsontools xmlTojson ERROR al leer el fichero y/o crear el json de " + path_xml)
        logger.info("pelisalacarta.core.jsontools " + traceback.format_exc())

    return ret


class Xml2Json:
    # http://code.activestate.com/recipes/577494-convert-xml-into-json-python-dicts-and-lists-struc/
    # >>> Xml2Json('<doc><tag><subtag>data</subtag><t>data1</t><t>data2</t></tag></doc>').result
    # {u'doc': {u'tag': {u'subtag': u'data', u't': [u'data1', u'data2']}}}
    LIST_TAGS = ['COMMANDS']

    def __init__(self, data=None):
        # print "################## INIT"
        from xml.parsers.expat import ParserCreate
        self._parser = ParserCreate()
        self._parser.StartElementHandler = self.start
        self._parser.EndElementHandler = self.end
        self._parser.CharacterDataHandler = self.data
        self.result = None
        if data:
            self.feed(data)
            self.close()

    def feed(self, data):
        # print "################## FEED"
        self._stack = []
        self._data = ''
        self._parser.Parse(data, 0)

    def close(self):
        self._parser.Parse("", 1)
        del self._parser
        # print "################## CLOSE"
        self.result = to_utf8(self.result)

    def start(self, tag, attrs):
        assert attrs == {}
        assert self._data.strip() == ''
        # print "START", repr(tag)
        self._stack.append([tag])
        self._data = ''

    def end(self, tag):
        # print "END", repr(tag)
        last_tag = self._stack.pop()
        assert last_tag[0] == tag
        if len(last_tag) == 1:  # leaf
            data = self._data
        else:
            if tag not in Xml2Json.LIST_TAGS:
                # build a dict, repeating pairs get pushed into lists
                data = {}
                for k, v in last_tag[1:]:
                    if k not in data:
                        data[k] = v
                    else:
                        el = data[k]
                        if type(el) is not list:
                            data[k] = [el, v]
                        else:
                            el.append(v)
            else:  # force into a list
                data = [{k: v} for k, v in last_tag[1:]]
        if self._stack:
            self._stack[-1].append((tag, data))
        else:
            self.result = {tag: data}
        self._data = ''

    def data(self, data):
        # print "################## DATA"
        self._data = data
