import json
import os
from flask import Flask, render_template, request, redirect, url_for, flash, session, abort
from werkzeug.utils import secure_filename

app = Flask(__name__)
app.secret_key = 'chave_secreta_atelie_croche'

UPLOAD_FOLDER = os.path.join(app.root_path, 'static', 'images', 'produtos')
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'webp'}
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

os.makedirs(UPLOAD_FOLDER, exist_ok=True)

ADMIN_PASSWORD = "admin"

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def carregar_produtos():
    caminho_json = os.path.join(app.root_path, 'data', 'produtos.json')
    if os.path.exists(caminho_json):
        with open(caminho_json, 'r', encoding='utf-8') as file:
            return json.load(file)
    return []

def salvar_produtos(produtos):
    caminho_json = os.path.join(app.root_path, 'data', 'produtos.json')
    with open(caminho_json, 'w', encoding='utf-8') as file:
        json.dump(produtos, file, ensure_ascii=False, indent=2)

@app.route('/')
def home():
    produtos = carregar_produtos()
    categorias = [
        {"slug": "amigurumis", "nome": "Amigurumis", "icone": "🧸"},
        {"slug": "mesa-posta", "nome": "Mesa Posta & Decoração", "icone": "🍽️"},
        {"slug": "moda-acessorios", "nome": "Moda & Acessórios", "icone": "👜"},
        {"slug": "linha-infantil", "nome": "Linha Infantil", "icone": "👶"}
    ]
    return render_template('index.html', produtos=produtos, categorias=categorias)

@app.route('/categoria/<string:slug>')
def categoria(slug):
    produtos_todos = carregar_produtos()
    produtos_filtrados = [p for p in produtos_todos if p['categoria'] == slug]
    
    nomes_map = {
        "amigurumis": "Amigurumis",
        "mesa-posta": "Mesa Posta & Decoração",
        "moda-acessorios": "Moda & Acessórios",
        "linha-infantil": "Linha Infantil"
    }
    nome_categoria = nomes_map.get(slug, "Categoria")
    
    return render_template('categoria.html', produtos=produtos_filtrados, slug=slug, nome_categoria=nome_categoria)

@app.route('/admin/login', methods=['GET', 'POST'])
def admin_login():
    if request.method == 'POST':
        senha_digitada = request.form.get('senha')
        if senha_digitada == ADMIN_PASSWORD:
            session['logged_in'] = True
            return redirect(url_for('admin_dashboard'))
        else:
            flash('Senha incorreta! Tente novamente.', 'error')
    return render_template('admin_login.html')

@app.route('/admin/logout')
def admin_logout():
    session.pop('logged_in', None)
    return redirect(url_for('admin_login'))

@app.route('/admin')
def admin_dashboard():
    if not session.get('logged_in'):
        return redirect(url_for('admin_login'))
    produtos = carregar_produtos()
    return render_template('admin_dashboard.html', produtos=produtos)

@app.route('/admin/produto/novo', methods=['POST'])
def admin_novo_produto():
    if not session.get('logged_in'):
        return redirect(url_for('admin_login'))
    
    nome = request.form.get('nome')
    codigo = request.form.get('codigo')
    categoria_slug = request.form.get('categoria')
    preco = request.form.get('preco')
    fio = request.form.get('fio')
    tempo = request.form.get('tempo')
    descricao = request.form.get('descricao')
    
    imagem_url = "https://via.placeholder.com/600x600?text=Sem+Foto"
    if 'imagem' in request.files:
        file = request.files['imagem']
        if file and file.filename != '' and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            nome_arquivo_final = f"{codigo.lower()}_{filename}"
            caminho_salvar = os.path.join(app.config['UPLOAD_FOLDER'], nome_arquivo_final)
            file.save(caminho_salvar)
            imagem_url = f"/static/images/produtos/{nome_arquivo_final}"

    nomes_map = {
        "amigurumis": "Amigurumis",
        "mesa-posta": "Mesa Posta & Decoração",
        "moda-acessorios": "Moda & Acessórios",
        "linha-infantil": "Linha Infantil"
    }

    produtos = carregar_produtos()
    novo_id = max([p['id'] for p in produtos], default=0) + 1
    
    novo_item = {
        "id": novo_id,
        "codigo": codigo.upper(),
        "nome": nome,
        "categoria": categoria_slug,
        "categoria_nome": nomes_map.get(categoria_slug, "Geral"),
        "preco": preco,
        "fio": fio,
        "tempo": tempo,
        "imagem": imagem_url,
        "descricao": descricao
    }
    
    produtos.insert(0, novo_item)
    salvar_produtos(produtos)
    flash('Peça cadastrada com sucesso!', 'success')
    return redirect(url_for('admin_dashboard'))

# ---- ROTA DE EDIÇÃO DE PRODUTO ----
@app.route('/admin/produto/editar/<int:produto_id>', methods=['GET', 'POST'])
def admin_editar_produto(produto_id):
    if not session.get('logged_in'):
        return redirect(url_for('admin_login'))
    
    produtos = carregar_produtos()
    produto = next((p for p in produtos if p['id'] == produto_id), None)
    
    if not produto:
        flash('Produto não encontrado!', 'error')
        return redirect(url_for('admin_dashboard'))
    
    if request.method == 'POST':
        produto['nome'] = request.form.get('nome')
        produto['codigo'] = request.form.get('codigo').upper()
        produto['categoria'] = request.form.get('categoria')
        
        nomes_map = {
            "amigurumis": "Amigurumis",
            "mesa-posta": "Mesa Posta & Decoração",
            "moda-acessorios": "Moda & Acessórios",
            "linha-infantil": "Linha Infantil"
        }
        produto['categoria_nome'] = nomes_map.get(produto['categoria'], "Geral")
        produto['preco'] = request.form.get('preco')
        produto['fio'] = request.form.get('fio')
        produto['tempo'] = request.form.get('tempo')
        produto['descricao'] = request.form.get('descricao')
        
        # Se enviou uma nova foto, substitui
        if 'imagem' in request.files:
            file = request.files['imagem']
            if file and file.filename != '' and allowed_file(file.filename):
                filename = secure_filename(file.filename)
                nome_arquivo_final = f"{produto['codigo'].lower()}_{filename}"
                caminho_salvar = os.path.join(app.config['UPLOAD_FOLDER'], nome_arquivo_final)
                file.save(caminho_salvar)
                produto['imagem'] = f"/static/images/produtos/{nome_arquivo_final}"
        
        salvar_produtos(produtos)
        flash('Peça atualizada com sucesso!', 'success')
        return redirect(url_for('admin_dashboard'))
        
    return render_template('admin_editar.html', produto=produto)

@app.route('/admin/produto/deletar/<int:produto_id>', methods=['POST'])
def admin_deletar_produto(produto_id):
    if not session.get('logged_in'):
        return redirect(url_for('admin_login'))
    
    produtos = carregar_produtos()
    produtos = [p for p in produtos if p['id'] != produto_id]
    salvar_produtos(produtos)
    
    flash('Peça removida com sucesso!', 'success')
    return redirect(url_for('admin_dashboard'))

if __name__ == '__main__':
    app.run(debug=True, port=5000)