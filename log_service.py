# coding: utf-8
import re
from flask import Flask, jsonify, request
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


@app.route('/logs', methods=['GET'])
def view_logs():
    # DB connection(logs)
    logs_connection = DataBase(DataBase.DB_URLS[u'logs'])
    # Create new session
    l_session = logs_connection.new_session()
    # Logs objects
    sql_base_logs = l_session.query(Log)

    # Filters
    filters = request.args.keys()
    if u'from' in filters:
        if float(request.args[u'from']) >= 0:
            sql_base_logs = sql_base_logs\
                .filter(Log.dt >= float(request.args[u'from']))

    if u'to' in filters:
        if float(request.args[u'to']) >= 0:
            sql_base_logs = sql_base_logs\
                .filter(Log.dt <= float(request.args[u'to']))

    # Page and items
    if (u'page' in filters) & (u'items' in filters):
        page_number = int(request.args[u'page']) - 1 if int(request.args[u'page']) != 0 else 0
        number_of_rows_per_page = int(request.args[u'items'])
        if (page_number >= 0) & (number_of_rows_per_page >= 0):
            sql_base_logs = sql_base_logs\
                .slice(page_number*number_of_rows_per_page, (page_number*number_of_rows_per_page)+number_of_rows_per_page)

    elif u'items' in filters:
        if int(request.args[u'items']) >= 0:
            sql_base_logs = sql_base_logs\
                .limit(int(request.args[u'items']))

    # Get logs from db
    _logs = sql_base_logs.all()
    # Pack log objects to json
    json_log = pack_log(_logs, full_names_(_logs))
    # Close opened session
    l_session.close()

    return jsonify(json_log)


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8000)