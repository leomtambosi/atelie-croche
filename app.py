import json
import os
from flask import Flask, render_template, abort

app = Flask(__name__)

def carregar_produtos():
    caminho_json = os.path.join(app.root_path, 'data', 'produtos.json')
    if os.path.exists(caminho_json):
        with open(caminho_json, 'r', encoding='utf-8') as file:
            return json.load(file)
    return []

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
    
    # Descobre o nome bonito da categoria com base no slug
    nomes_map = {
        "amigurumis": "Amigurumis",
        "mesa-posta": "Mesa Posta & Decoração",
        "moda-acessorios": "Moda & Acessórios",
        "linha-infantil": "Linha Infantil"
    }
    nome_categoria = nomes_map.get(slug, "Categoria")
    
    return render_template('categoria.html', produtos=produtos_filtrados, slug=slug, nome_categoria=nome_categoria)

if __name__ == '__main__':
    app.run(debug=True, port=5000)