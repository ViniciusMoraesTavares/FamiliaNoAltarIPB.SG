from src.painel import iniciar_painel
from src.data_manager import DataManager
from src.version import APP_VERSION
import os
import sys

def criar_atalho_na_area_de_trabalho(nome_atalho="Família no Altar"):
    try:
        import win32com.client
        desktop = os.path.join(os.path.join(os.environ['USERPROFILE']), 'Desktop')
        caminho_atalho = os.path.join(desktop, f"{nome_atalho}.lnk")

        if not os.path.exists(caminho_atalho):
            shell = win32com.client.Dispatch("WScript.Shell")
            atalho = shell.CreateShortcut(caminho_atalho)
            atalho.TargetPath = sys.executable
            atalho.WorkingDirectory = os.path.dirname(sys.executable)

            icone_path = os.path.join(os.path.dirname(sys.executable), "icone.ico")
            if os.path.exists(icone_path):
                atalho.IconLocation = icone_path
            else:
                atalho.IconLocation = sys.executable

            atalho.save()
    except Exception as e:
        print(f"Erro ao criar atalho: {e}")

if __name__ == '__main__':
    if getattr(sys, 'frozen', False):
        criar_atalho_na_area_de_trabalho()
    try:
        DataManager().executar_validacao_inicial()
    except Exception:
        pass
    try:
        DataManager().backup_auto_se_versao_mudou(APP_VERSION)
    except Exception:
        pass
    iniciar_painel()
