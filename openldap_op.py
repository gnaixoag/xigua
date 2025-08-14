import ldap3
from ldap3 import Server, Connection, ALL, MODIFY_REPLACE
from flask import Flask, request, jsonify

app = Flask(__name__)

LDAP_SERVER = 'ldap://your-ldap-server'
LDAP_USER_DN = 'cn=admin,dc=example,dc=com'
LDAP_PASSWORD = 'admin_password'
BASE_DN = 'ou=users,dc=example,dc=com'

def get_ldap_conn():
    server = Server(LDAP_SERVER, get_info=ALL)
    conn = Connection(server, LDAP_USER_DN, LDAP_PASSWORD, auto_bind=True)
    return conn

@app.route('/user', methods=['POST'])
def create_user():
    data = request.json
    uid = data['uid']
    user_dn = f'uid={uid},{BASE_DN}'
    attributes = {
        'objectClass': ['inetOrgPerson', 'posixAccount', 'top'],
        'uid': uid,
        'sn': data.get('sn', uid),
        'cn': data.get('cn', uid),
        'userPassword': data['password'],
        'uidNumber': data.get('uidNumber', '10000'),
        'gidNumber': data.get('gidNumber', '10000'),
        'homeDirectory': f"/home/{uid}"
    }
    conn = get_ldap_conn()
    try:
        conn.add(user_dn, attributes=attributes)
        if conn.result['description'] == 'success':
            return jsonify({'msg': 'User created'}), 201
        else:
            return jsonify({'error': conn.result['description']}), 400
    finally:
        conn.unbind()

@app.route('/user/<uid>', methods=['DELETE'])
def delete_user(uid):
    user_dn = f'uid={uid},{BASE_DN}'
    conn = get_ldap_conn()
    try:
        conn.delete(user_dn)
        if conn.result['description'] == 'success':
            return jsonify({'msg': 'User deleted'}), 200
        else:
            return jsonify({'error': conn.result['description']}), 400
    finally:
        conn.unbind()

@app.route('/user/<uid>/password', methods=['PUT'])
def change_password(uid):
    data = request.json
    new_password = data['password']
    user_dn = f'uid={uid},{BASE_DN}'
    conn = get_ldap_conn()
    try:
        conn.modify(user_dn, {'userPassword': [(MODIFY_REPLACE, [new_password])]})
        if conn.result['description'] == 'success':
            return jsonify({'msg': 'Password changed'}), 200
        else:
            return jsonify({'error': conn.result['description']}), 400
    finally:
        conn.unbind()

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8080)