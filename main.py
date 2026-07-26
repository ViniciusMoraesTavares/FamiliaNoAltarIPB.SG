from src.painel import iniciar_painel
from src.data_manager import DataManager
from src.icon import apply_windows_app_user_model_id
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
            atalho.IconLocation = f"{sys.executable},0"

            atalho.save()
    except Exception as e:
        print(f"Erro ao criar atalho: {e}")

if __name__ == '__main__':
    apply_windows_app_user_model_id()
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
