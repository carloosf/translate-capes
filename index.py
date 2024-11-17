import json
from flask import Flask, request, jsonify
from googletrans import Translator
from flask_swagger_ui import get_swaggerui_blueprint

app = Flask(__name__)
translator = Translator()

try:
    with open('db.json', 'r', encoding='utf-8') as f:
        data = json.load(f)
except FileNotFoundError:
    data = []

SWAGGER_URL = '/swagger'
API_URL = '/static/swagger.json'
swaggerui_blueprint = get_swaggerui_blueprint(
    SWAGGER_URL,
    API_URL,
    config={
        'app_name': "Translate API"
    }
)
app.register_blueprint(swaggerui_blueprint, url_prefix=SWAGGER_URL)

@app.route('/api/search', methods=['GET'])
def search_content():
    query = request.args.get('query', '')
    print(f"Query recebida: {query}")

    if not query:
        return jsonify({"error": "O termo de pesquisa 'query' é obrigatório."}), 400

    try:
        query_lang = translator.detect(query).lang
        print(f"Idioma detectado para '{query}': {query_lang}")
    except Exception as e:
        return jsonify({"error": f"Erro ao detectar idioma: {str(e)}"}), 500

    results = []
    for item in data:
        try:
            src_lang = item['idioma'].lower()
            if src_lang == 'português':
                src_lang = 'pt'
            elif src_lang == 'inglês':
                src_lang = 'en'
            elif src_lang == 'espanhol':
                src_lang = 'es'

            translated_title = translator.translate(
                item['titulo'], src=src_lang, dest=query_lang).text
            translated_content = translator.translate(
                item['conteudo'], src=src_lang, dest=query_lang).text

            print(f"Título traduzido: {translated_title}")
            print(f"Conteúdo traduzido: {translated_content}")

            if query.lower() in translated_title.lower() or query.lower() in translated_content.lower():
                print(f"Termo '{query}' encontrado no item com ID {item['id']}")
                results.append({
                    "original": item,
                    "translated_title": translated_title,
                    "translated_content": translated_content
                })
            else:
                print(f"Termo '{query}' não encontrado no item com ID {item['id']}")
        except Exception as e:
            print(f"Erro ao traduzir item {item['id']}: {str(e)}")
            continue

    print(f"Resultados encontrados: {len(results)}")
    return jsonify(results)

if __name__ == '__main__':
    app.run(debug=True)
