import requests
import time
import win32print
import os
import json

# ================= CONFIGURAÇÃO =================
# Coloque aqui SOMENTE a base do seu site (sem /webhook)
URL_BASE = "https://api-impressora.onrender.com"
ARQUIVO_CONFIG = "config.txt"
# ================================================

def ler_configuracao():
    """Lê o arquivo config.txt para saber quem sou eu"""
    if not os.path.exists(ARQUIVO_CONFIG):
        print(f"\n[ERRO] O arquivo '{ARQUIVO_CONFIG}' não existe!")
        print("Crie um arquivo config.txt na mesma pasta com:")
        print("LINHA 1: nome-da-loja (igual ao webhook)")
        print("LINHA 2: Nome da Impressora")
        time.sleep(10)
        return None, None
        
    try:
        with open(ARQUIVO_CONFIG, "r", encoding="utf-8") as f:
            linhas = f.readlines()
            # Remove espaços e quebras de linha extras
            cliente_id = linhas[0].strip()
            impressora = linhas[1].strip()
            return cliente_id, impressora
    except Exception as e:
        print(f"[ERRO] Falha ao ler config.txt: {e}")
        return None, None

def imprimir_cupom(conteudo, nome_impressora):
    try:
        hPrinter = win32print.OpenPrinter(nome_impressora)
        try:
            hJob = win32print.StartDocPrinter(hPrinter, 1, ("Cupom Bot", None, "RAW"))
            win32print.StartPagePrinter(hPrinter)
            
            # Comandos ESC/POS
            CMD_INIT        = b'\x1b\x40'
            CMD_CENTRALIZAR = b'\x1b\x61\x01'
            CMD_ESQUERDA    = b'\x1b\x61\x00'
            CMD_NEGRITO_ON  = b'\x1b\x45\x01'
            CMD_NEGRITO_OFF = b'\x1b\x45\x00'
            CMD_CORTE       = b'\x1d\x56\x00'
            
            # --- IMPRESSÃO ---
            win32print.WritePrinter(hPrinter, CMD_INIT)
            win32print.WritePrinter(hPrinter, CMD_CENTRALIZAR + CMD_NEGRITO_ON)
            win32print.WritePrinter(hPrinter, "=== NOVO PEDIDO ===\n\n".encode("cp850"))
            win32print.WritePrinter(hPrinter, CMD_NEGRITO_OFF + CMD_ESQUERDA)
            
            # Corpo do Texto
            texto_final = str(conteudo)
            win32print.WritePrinter(hPrinter, texto_final.encode("cp850", errors="ignore"))
            
            # Rodapé
            win32print.WritePrinter(hPrinter, b"\n\n-------------------\n\n\n\n\n")
            win32print.WritePrinter(hPrinter, CMD_CORTE)
            
            win32print.EndPagePrinter(hPrinter)
            win32print.EndDocPrinter(hPrinter)
            print(" >> [SUCESSO] Impresso com sucesso!")
            
        finally:
            win32print.ClosePrinter(hPrinter)
    except Exception as e:
        print(f" >> [ERRO IMPRESSORA] {e}")
        print("Verifique se o nome no config.txt está EXATO.")

def iniciar():
    print("--- SISTEMA DE IMPRESSÃO MULTI-LOJA ---")
    
    # 1. Carrega as configurações
    meu_id, minha_impressora = ler_configuracao()
    
    if not meu_id or not minha_impressora:
        print("Configuração inválida. Fechando...")
        time.sleep(5)
        return

    print(f"LOJA IDENTIFICADA: {meu_id}")
    print(f"IMPRESSORA ALVO:   {minha_impressora}")
    print("Iniciando monitoramento...")

    # Loop Infinito
    while True:
        try:
            # Busca SOMENTE na caixinha dessa loja
            url = f"{URL_BASE}/buscar_pedido/{meu_id}"
            response = requests.get(url, timeout=10)
            
            if response.status_code == 200:
                dados = response.json()
                
                # Se tiver dados (dicionário não vazio)
                if dados:
                    print(f"\n[RECEBIDO] Pedido encontrado!")
                    
                    # Pega o texto independente da chave
                    chave = list(dados.keys())[0]
                    texto = dados[chave]
                    
                    imprimir_cupom(texto, minha_impressora)
            
        except Exception as e:
            print(f"Erro de conexão: {e}")
            
        time.sleep(5)

if __name__ == "__main__":
    iniciar()
