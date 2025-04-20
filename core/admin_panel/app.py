from flask import Flask, render_template, request, redirect, url_for, flash
from flask_sqlalchemy import SQLAlchemy
from flask_bcrypt import Bcrypt
from flask_login import LoginManager, UserMixin, login_user, login_required, logout_user, current_user
from dotenv import load_dotenv
import os, sys

# Carregar variáveis do arquivo .env (na raiz do projeto)
load_dotenv()

# bcrypt = Bcrypt()
# password = "admin123"
# password_hash = bcrypt.generate_password_hash(password).decode('utf-8')
# print(f"Password hash: {password_hash}")
# sys.exit(1)

# Inicializando o Flask, banco de dados (SQLAlchemy), bcrypt para segurança de senhas e login
app = Flask(__name__)

# Configurações do app e banco de dados
app.config['SECRET_KEY'] = os.getenv('FLASK_SECRET_KEY')
app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv('DATABASE_URL') + '?client_encoding=UTF8'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False  # Desabilitar o rastreamento de modificações, evitando overhead
app.secret_key = 'your_flask_secret_key'

# Inicializando SQLAlchemy, Bcrypt e Flask-Login
db = SQLAlchemy(app)
bcrypt = Bcrypt(app)
login_manager = LoginManager(app)
login_manager.login_view = 'login'

# Modelo de Usuário para o banco de dados
class User(UserMixin, db.Model):
    __tablename__ = 'users'  # Usar o nome da tabela corretamente
    __table_args__ = {'schema': 'labsync'}  # Especificar o schema 'labsync'
    
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(100), unique=True, nullable=False)
    password_hash = db.Column(db.String(200), nullable=False)

# Carregar usuário pelo ID
@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

# Rota inicial que redireciona para a página de login
@app.route('/')
def home():
    if current_user.is_authenticated:
        return redirect(url_for('dashboard'))  # Redireciona para o dashboard se já estiver logado
    return redirect(url_for('login'))  # Redireciona para o login se não estiver logado


# Rota de login
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        print(f"Username recebido: {username}")
        print(f"Password recebido: {password}")

        # Buscar usuário no banco de dados
        user = User.query.filter_by(username=username).first()

        if user and bcrypt.check_password_hash(user.password_hash, password):
            # Login bem-sucedido, cria a sessão do usuário
            login_user(user)
            return redirect(url_for('dashboard'))  # Redireciona para o painel após o login bem-sucedido
        else:
            flash('Login inválido. Verifique as credenciais.', 'danger')

    return render_template('login.html')  # Renderiza o template de login

@app.route('/create_user', methods=['GET', 'POST'])
@login_required  # Garante que apenas usuários logados possam criar novos usuários
def create_user():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        password_hash = bcrypt.generate_password_hash(password).decode('utf-8')

        # Criar um novo usuário
        new_user = User(username=username, password_hash=password_hash)

        try:
            db.session.add(new_user)
            db.session.commit()
            flash('Usuário criado com sucesso!', 'success')
            
            # Se o usuário já estiver logado, redirecionar diretamente para o dashboard
            if current_user.is_authenticated:
                return redirect(url_for('dashboard'))
            
            return redirect(url_for('login'))  # Caso o usuário não esteja logado, redireciona para o login
        except Exception as e:
            db.session.rollback()
            flash(f'Erro ao criar usuário: {e}', 'danger')

    return render_template('create_user.html')  # Formulário para criação de usuários


@app.route('/change_password', methods=['GET', 'POST'])
@login_required
def change_password():
    if request.method == 'POST':
        old_password = request.form['old_password']
        new_password = request.form['new_password']

        user = current_user
        if bcrypt.check_password_hash(user.password_hash, old_password):
            user.password_hash = bcrypt.generate_password_hash(new_password).decode('utf-8')

            try:
                db.session.commit()
                flash('Senha alterada com sucesso!', 'success')
                return redirect(url_for('dashboard'))
            except Exception as e:
                db.session.rollback()
                flash(f'Erro ao alterar senha: {e}', 'danger')
        else:
            flash('Senha antiga incorreta', 'danger')

    return render_template('change_password.html')  # Formulário para alteração de senha


# Rota do painel (após login)
@app.route('/dashboard')
@login_required  # Garante que a página só pode ser acessada se o usuário estiver logado
def dashboard():
    return render_template('dashboard.html')  # Renderiza o template do painel

# Rota de logout
@app.route('/logout')
@login_required
def logout():
    logout_user()  # Faz o logout do usuário
    return redirect(url_for('login'))  # Redireciona para a página de login após o logout

if __name__ == "__main__":
    app.run(debug=True, host='0.0.0.0', port=5000)
