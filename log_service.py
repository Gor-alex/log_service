# coding=utf-8
# -*- coding: utf-8 -*-
import re
from flask import Flask, jsonify, request, abort
from validators.logs import LogUrl
# DB
from sys_funcs.databases import DataBase
# Models
from model.people import Person
from model.logs import Log

app = Flask(__name__)


def get_unic_id_person(_logs):
    '''

    :param _logs: [logs obj]
        logs nodes
    :return: set()
        set of id peoples
    '''
    names = set()
    for l_node in _logs:
        names.update(l_node.persons)

    return names


def full_names_(_logs):
    '''

    :param _logs: []
        List with model.Logs
    :return: dict()
        dict() of full names (Only active names)
    '''
    # DB connection(people)
    person_connection = DataBase(DataBase.DB_URLS[u'people'])
    l_session = person_connection.new_session()
    # All active persons
    persons = l_session.query(Person)\
        .filter(Person.id.in_(get_unic_id_person(_logs))).all()
    # Pack names to dict
    names = dict()
    for person in persons:
        names[person.id] = person.full_name

    # Close opened session
    l_session.close()
    return names


def pack_log(_logs, names):
    '''

    :param _logs: []
        List with model.Logs
    :param names: dict()
        dict() of full names (Only active names)
    :return: dict()
        dict for json answer

    '''
    json = list()
    for log_unit in _logs:
        # Event text
        _text = log_unit.event
        # Finding nodes to replecing
        nodes = re.findall(r'(<p=)(\d+)(>)', _text)
        # Replacement of all occurrences on names
        for node in nodes:
            # Name for replace
            name = names[int(node[1])]
            # Replacing template on name
            _text = _text.replace(u''.join(node), name)

        json.append(
            {
                u'event': _text,
                u'date': int(log_unit.dt),
                # u'id': log_unit.id
            }
        )

    return json


def validation_url(view):
    def valid_it():
        # Instance schema
        schema = LogUrl()
        # Create field in request for valid values
        request.validated = {}
        # Valid items
        try:
            request.validated.update(
                schema.deserialize(dict(request.args.items()))
            )
        except Exception as error:
            abort(500, description=str(error))

        return view()

    return valid_it


@app.route('/logs', methods=['GET'])
@validation_url
def view_logs():
    # DB connection(logs)
    logs_connection = DataBase(DataBase.DB_URLS[u'logs'])
    # Create new session
    l_session = logs_connection.new_session()

    # Main sql object
    sql_base_logs = l_session.query(Log)
    if hasattr(request, 'validated'):
        filters = request.validated.keys()

        if u'from' in filters:
            sql_base_logs = sql_base_logs.filter(Log.dt >= request.validated[u'from'])

        if u'to' in filters:
            sql_base_logs = sql_base_logs.filter(Log.dt <= request.validated[u'to'])

        # Page and items
        if (u'page' in filters) & (u'items' in filters):
            # Pages starts from 1
            page_number = request.validated[u'page'] - 1 if request.validated[u'page'] != 0 else 0
            # items on page
            items_on_page = request.validated[u'items']
            # Add filter
            sql_base_logs = sql_base_logs.slice(page_number*items_on_page, (page_number*items_on_page)+items_on_page)

        elif u'items' in filters:
            sql_base_logs = sql_base_logs.limit(request.validated[u'items'])

        # Get logs from db
        _logs = sql_base_logs.all()
        # Pack log objects to json
        json_log = pack_log(_logs, full_names_(_logs))
        # Close opened session
        l_session.close()

        return jsonify(json_log)
    else:
        abort(500, description='Not valid filters in url')


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8000)