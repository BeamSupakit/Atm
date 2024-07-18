from flask import Flask, render_template, request, redirect, url_for, flash
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)
app.config['SECRET_KEY'] = '2asfdqegqegqgqwqwdwvbvjvcg'
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://root:@localhost/atm'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)

class Account(db.Model):
    account_number = db.Column(db.String(50), primary_key=True)
    username = db.Column(db.String(50), nullable=False)
    balance = db.Column(db.Float, nullable=False)

    def __init__(self, account_number, username, balance):
        self.account_number = account_number
        self.username = username
        self.balance = balance

with app.app_context():
    db.create_all()

@app.route('/')
def index():
    accounts = Account.query.all()
    return render_template('index.html', accounts=accounts)

@app.route('/create_account', methods=['GET', 'POST'])
def create_account():
    if request.method == 'POST':
        account_number = request.form['account_number']
        username = request.form['username']
        try:
            balance = float(request.form['balance'])
        except ValueError:
            flash('กรุณากรอกยอดคงเหลือเริ่มต้นให้ถูกต้อง', 'danger')
            return redirect(url_for('create_account'))

        if balance < 0:
            flash('ยอดคงเหลือเริ่มต้นไม่สามารติดค่าลบได้', 'danger')
            return redirect(url_for('create_account'))

        existing_account = Account.query.filter_by(account_number=account_number).first()
        if existing_account:
            flash('เลขบัญชีนี้มีอยู่แล้ว กรุณาใช้เลขบัญชีอื่น', 'danger')
            return redirect(url_for('create_account'))

        new_account = Account(account_number, username, balance)
        db.session.add(new_account)
        db.session.commit()
        flash('สร้างบัญชีใหม่สำเร็จแล้ว', 'success')
        return redirect(url_for('index'))

    return render_template('create_account.html')

@app.route('/account/<account_number>', methods=['GET', 'POST'])
def account(account_number):
    account = Account.query.filter_by(account_number=account_number).first()
    if not account:
        return 'Account not found', 404

    if request.method == 'POST':
        action = request.form['action']
        amount = float(request.form['amount'])

        if action == 'deposit':
            account.balance += amount
        elif action == 'withdraw' and account.balance >= amount:
            account.balance -= amount
        else:
            return 'Invalid operation', 400

        db.session.commit()
        return redirect(url_for('account', account_number=account_number))

    return render_template('account.html', account=account)

@app.route('/delete_account/<account_number>', methods=['POST'])
def delete_account(account_number):
    account = Account.query.filter_by(account_number=account_number).first()
    if account:
        db.session.delete(account)
        db.session.commit()
    return redirect(url_for('index'))

if __name__ == '__main__':
    app.run(debug=True)
