from flask import Flask, request, jsonify
import os
import json

app = Flask(__name__)

# MEMÓRIA MULTI-CLIENTE
# Exemplo: { 'pizzaria-do-beto': [pedido1], 'loja-da-maria': [pedido2] }
filas_de_pedidos = {}

@app.route('/')
def index():
    return "Servidor Multi-Clientes Online!"

# --- ROTA DE RECEBIMENTO (WEBHOOK) ---
# O Bot manda para: .../webhook/nome-da-loja
@app.route('/webhook/<cliente_id>', methods=['POST'])
def receber_webhook(cliente_id):
    try:
        # 1. Garante que a caixa de correio dessa loja existe
        if cliente_id not in filas_de_pedidos:
            filas_de_pedidos[cliente_id] = []
            
        dados = request.json
        print(f"--- [NOVO] Pedido para: {cliente_id} ---", flush=True)

        # 2. LIMPEZA E FORMATAÇÃO (Igual fizemos antes)
        conteudo = dados.get('cupom') or dados.get('message') or dados.get('text')
        
        # Tira da lista se vier como ['texto']
        if isinstance(conteudo, list) and len(conteudo) > 0:
            texto_base = str(conteudo[0])
        else:
            texto_base = str(conteudo)

        # Formatação Visual (Quebras de linha)
        texto_formatado = texto_base.replace("\\n", "\n")
        texto_formatado = texto_formatado.replace("Telefone:", "\nTelefone:")
        texto_formatado = texto_formatado.replace("Endereço:", "\nEndereço:")
        texto_formatado = texto_formatado.replace("Pedido (", "\n--------------------------------\nPedido (")
        texto_formatado = texto_formatado.replace("Valor total:", "\n\nValor total:")
        texto_formatado = texto_formatado.replace("Forma de pagamento:", "\nForma de pagamento:")
        texto_formatado = texto_formatado.replace("Observações", "\n--------------------------------\nObservações")

        # 3. Guarda na fila ESPECÍFICA da loja
        filas_de_pedidos[cliente_id].append({"texto": texto_formatado})
        
        return jsonify({"status": "sucesso", "loja": cliente_id}), 200

    except Exception as e:
        print(f"ERRO: {e}")
        return jsonify({"status": "erro", "detalhes": str(e)}), 500

# --- ROTA DE BUSCA (PC DO CLIENTE) ---
# O PC busca em: .../buscar_pedido/nome-da-loja
@app.route('/buscar_pedido/<cliente_id>', methods=['GET'])
def entregar_para_pc(cliente_id):
    # Verifica se a loja existe e se tem pedidos
    if cliente_id in filas_de_pedidos and filas_de_pedidos[cliente_id]:
        # Entrega o pedido e remove da fila
        return jsonify(filas_de_pedidos[cliente_id].pop(0))
    
    return jsonify({}) # Retorna vazio se não tiver nada
