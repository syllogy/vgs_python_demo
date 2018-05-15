import json
import sys
import traceback
from datetime import datetime

from flask import render_template, request, Blueprint, flash
from flask_admin import Admin, expose
from flask_admin.actions import action
from flask_admin.contrib.sqla import ModelView

import processor
import persistence


db = persistence.db
bp = Blueprint('payment', __name__)


@bp.route('/', methods=["GET"])
def index():
    url = request.args.get('url', 'becomeverygood.com')
    return render_template('payment.html', url=url)


@bp.route('/payment', methods=["POST"])
def create():
    imm = request.values
    dic = imm.to_dict(flat=True)
    payment_entry = Payment.from_dict(dic)
    db.session.add(payment_entry)
    db.session.commit()
    json_data = json.dumps(dic)
    print(json_data)
    return render_template('show_redacted.html', data=dic, url=dic['url'])


class Payment(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    name = db.Column(db.String(100))
    billing_address = db.Column(db.String(100))
    card_number = db.Column(db.String(100))
    card_expiration = db.Column(db.String(100))
    card_security_code = db.Column(db.String(100))

    @classmethod
    def from_dict(cls, kwargs):
        payment_obj = cls()
        payment_obj.name = kwargs['name']
        payment_obj.billing_address = kwargs['billing_address']
        payment_obj.card_number = kwargs['card-number']
        payment_obj.card_expiration = kwargs['card-expiration-date']
        payment_obj.card_security_code = kwargs['card-security-code']
        return payment_obj

    def charge(self):
        response = processor.charge({
            'card': self.card_number,
            'card_expiration': self.card_expiration,
            'card_security_code': self.card_security_code,
            'amount': 10000})
        response.raise_for_status()
        print(response.json())
        return True


class CustomView(ModelView):
    list_template = 'merchant/list.html'
    create_template = 'merchant/create.html'
    edit_template = 'merchant/edit.html'


class PaymentAdmin(CustomView):

    @action('charge', 'Charge', 'Are you sure you want to charge this card?')
    def action_charge(self, ids):
        try:
            query = Payment.query.filter(Payment.id.in_(ids))
            count = 0
            for payment_entry in query.all():
                payment_entry.charge()
                count += 1
            flash('{count} cards were charged successfully. '.format(count=count))
        except Exception as ex:
            print(''.join(traceback.format_exception(None, ex, ex.__traceback__)),
                  file=sys.stderr, flush=True)
            flash('Failed to approve users. {error}'.format(
                error=ex), category='error')


def init_app(app):
    app.register_blueprint(bp)
    merchant_admin = Admin(app,
                           url='/merchant_admin',
                           name='Merchant Portal',
                           base_template='merchant/layout.html',
                           template_mode='bootstrap2')
    merchant_admin.add_view(PaymentAdmin(
        Payment, db.session, endpoint='payments'))
    return app
