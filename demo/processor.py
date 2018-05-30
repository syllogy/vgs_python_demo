import requests

from datetime import datetime
from urllib.parse import urljoin, urlunsplit
from flask import Blueprint, current_app, request
from flask_admin import Admin
from flask_admin.contrib.sqla import ModelView

import helpers as h
import persistence

db = persistence.db
bp = Blueprint('processor', __name__)

@bp.route('/charge', methods=('POST',))
def create_charge():
    """Returns POST Data."""
    extracted = h.get_dict(
        'url', 'args', 'form', 'data', 'origin', 'headers', 'files', 'json')
    charge_entry = Charge.from_dict(extracted['json'])
    db.session.add(charge_entry)
    db.session.commit()
    return h.jsonify(extracted)


def charge(payload):
    root_url = current_app.config['VGS_PROCESSOR_ROOT_URL']
    url = urljoin(root_url, '/charge')
    proxies = {}
    if 'VGS_PROXY_URL' in current_app.config:
        proxies['https'] = urlunsplit(
            ('https',
             '{PROXY_USERNAME}:{PROXY_PASSWORD}@{PROXY_URL}:{PROXY_PORT}'.format(
                 PROXY_USERNAME=current_app.config['VGS_PROXY_USERNAME'],
                 PROXY_PASSWORD=current_app.config['VGS_PROXY_PASSWORD'],
                 PROXY_URL=current_app.config['VGS_PROXY_URL'],
                 PROXY_PORT=current_app.config['VGS_PROXY_PORT']
             ),
             '', None, None))

    r = requests.post(
        url,
        data=h.dumps(payload),
        headers={"Content-type": "application/json"},
        proxies=proxies,
        verify='demo/static/cert.pem'
    )
    return r

class Charge(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    card_number = db.Column(db.String(100))
    card_expiration = db.Column(db.String(100))
    card_security_code = db.Column(db.String(100))
    amount = db.Column(db.Integer)

    @classmethod
    def from_dict(cls, entry):
        charge_obj = cls()
        charge_obj.card_number = entry['card']
        charge_obj.card_expiration = entry['card_expiration']
        charge_obj.card_security_code = entry['card_security_code']
        charge_obj.amount = entry['amount']
        return charge_obj


class ChargeView(ModelView):
    pass


def init_app(app):
    app.register_blueprint(bp)
    app.json_encoder = h.JSONEncoder

    processor_admin = Admin(app,
                            url='/processor_admin',
                            endpoint='/processor_admin',
                            name='Processor Portal',
                            base_template='processor/admin/base.html',
                            template_mode='bootstrap3')

    processor_admin.add_view(ChargeView(
        Charge, db.session, endpoint='charges'))
    return app
