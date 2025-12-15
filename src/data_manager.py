import json
import os
import shutil
import random
import sys
import logging
import re
from uuid import uuid4

# Configuração de logging (pode ser adaptado para exibir na interface se quiser)
logging.basicConfig(level=logging.INFO)

def get_resource_path(*paths):
    """Retorna o caminho absoluto ao recurso, considerando empacotamento."""
    base_path = getattr(sys, '_MEIPASS', os.path.abspath('.'))
    return os.path.join(base_path, *paths)

class DataManager:
    _instance = None
    _familias_cache = None
    _ultimo_sorteio_cache = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(DataManager, cls).__new__(cls)
        return cls._instance

    def __init__(self, base_path_override=None):
        if base_path_override:
            self.base_path_data = base_path_override
            self.base_path_res = base_path_override
        else:
            if getattr(sys, 'frozen', False):
                self.base_path_data = os.path.dirname(sys.executable)
                self.base_path_res = getattr(sys, '_MEIPASS', os.path.abspath('.'))
            else:
                self.base_path_data = os.path.abspath('.')
                self.base_path_res = self.base_path_data

        self.base_path = self.base_path_data
        self.familias_file = os.path.join(self.base_path_data, "dados", "familias.json")
        self.sorteio_file = os.path.join(self.base_path_data, "dados", "sorteio.json")

        os.makedirs(os.path.join(self.base_path_data, "dados"), exist_ok=True)
        os.makedirs(os.path.join(self.base_path_data, "imagens", "familias"), exist_ok=True)
        os.makedirs(os.path.join(self.base_path_data, "imagens", "thumbs"), exist_ok=True)

        self._initialize_persistent_store()

    def _resource_path(self, *paths):
        return os.path.join(self.base_path_data, *paths)

    def _bundle_resource_path(self, *paths):
        return os.path.join(self.base_path_res, *paths)

    def _initialize_persistent_store(self):
        try:
            # Copiar dados iniciais do bundle se não existir persistente
            if not os.path.exists(self.familias_file):
                src = self._bundle_resource_path("dados", "familias.json")
                if os.path.exists(src):
                    shutil.copy2(src, self.familias_file)
                else:
                    self._atomic_write(self.familias_file, [])
            # Copiar imagens iniciais se não existirem
            src_imgs = self._bundle_resource_path("imagens", "familias")
            dst_imgs = os.path.join(self.base_path_data, "imagens", "familias")
            if os.path.exists(src_imgs):
                for name in os.listdir(src_imgs):
                    s = os.path.join(src_imgs, name)
                    d = os.path.join(dst_imgs, name)
                    try:
                        if os.path.isfile(s) and not os.path.exists(d):
                            shutil.copy2(s, d)
                    except Exception:
                        pass
        except Exception:
            pass

    def _normalize_familia(self, f):
        foto = f.get("foto")
        if foto:
            if os.path.isabs(foto):
                try:
                    rel = os.path.relpath(foto, self.base_path)
                    f["foto"] = rel.replace("\\", "/")
                except Exception:
                    pass
            else:
                f["foto"] = foto.replace("\\", "/")
        return f

    def _atomic_write(self, path, data):
        dir_path = os.path.dirname(path)
        os.makedirs(dir_path, exist_ok=True)
        tmp_path = os.path.join(dir_path, f".{os.path.basename(path)}.tmp")
        with open(tmp_path, "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
        os.replace(tmp_path, path)

    def carregar_familias(self, force_reload=False):
        if self._familias_cache is not None and not force_reload:
            return self._familias_cache

        try:
            if not os.path.exists(self.familias_file):
                self._familias_cache = []
                return []

            with open(self.familias_file, "r", encoding="utf-8") as f:
                dados = json.load(f)
                familias = [f for f in dados if "nome" in f and "numero" in f]
                familias = [self._normalize_familia(dict(f)) for f in familias]
                self._familias_cache = familias
                return familias
        except json.JSONDecodeError:
            logging.error(f"Erro ao decodificar {self.familias_file}")
            return []
        except Exception as e:
            logging.error(f"Erro ao carregar famílias: {str(e)}")
            return []

    def salvar_familias(self, familias):
        try:
            familias_norm = [self._normalize_familia(dict(f)) for f in familias]
            self._atomic_write(self.familias_file, familias_norm)
            self._familias_cache = familias_norm
            return True
        except Exception as e:
            logging.error(f"Erro ao salvar famílias: {str(e)}")
            return False

    def carregar_ultimo_sorteio(self, force_reload=False):
        if self._ultimo_sorteio_cache is not None and not force_reload:
            return self._ultimo_sorteio_cache

        try:
            if not os.path.exists(self.sorteio_file):
                return self._recalcular_ultimo_sorteado()

            with open(self.sorteio_file, "r", encoding="utf-8") as f:
                dados = json.load(f)
                num = dados.get("ultimo_sorteado")
                familias = self.carregar_familias()
                valido = any(str(f.get("numero")) == str(num) and f.get("sorteado") for f in familias)
                if not valido:
                    return self._recalcular_ultimo_sorteado()
                self._ultimo_sorteio_cache = num
                return num
        except json.JSONDecodeError:
            logging.error(f"Erro ao decodificar {self.sorteio_file}")
            return self._recalcular_ultimo_sorteado()
        except Exception as e:
            logging.error(f"Erro ao carregar último sorteio: {str(e)}")
            return self._recalcular_ultimo_sorteado()

    def salvar_sorteio(self, numero):
        try:
            self._atomic_write(self.sorteio_file, {"ultimo_sorteado": numero})
            self._ultimo_sorteio_cache = numero
            return True
        except Exception as e:
            logging.error(f"Erro ao salvar sorteio: {str(e)}")
            return False

    def resetar_sorteio(self):
        familias = self.carregar_familias()
        total_familias = len(familias)

        numeros_disponiveis = list(range(1, total_familias + 1))
        random.shuffle(numeros_disponiveis)

        for i, familia in enumerate(familias):
            familia["sorteado"] = False
            familia["numero"] = numeros_disponiveis[i]
            familia.pop("data_sorteio", None)

        if self.salvar_familias(familias):
            if os.path.exists(self.sorteio_file):
                os.remove(self.sorteio_file)
            self._ultimo_sorteio_cache = None
            return True
        return False

    def _valid_image_ext(self, path):
        ext = os.path.splitext(path)[-1].lower()
        return ext in {".png", ".jpg", ".jpeg"}

    def _resolve_photo_abs(self, relative_or_abs):
        if os.path.isabs(relative_or_abs):
            return relative_or_abs
        return self._resource_path(relative_or_abs)

    def adicionar_familia(self, nome, caminho_foto):
        nome = (nome or "").strip()
        if not nome:
            return False
        if not caminho_foto or not os.path.exists(caminho_foto) or not self._valid_image_ext(caminho_foto):
            return False

        familias = self.carregar_familias()
        novo_id = max([f.get("id", 0) for f in familias], default=0) + 1
        numero = max([f.get("numero", 0) for f in familias], default=0) + 1

        extensao = os.path.splitext(caminho_foto)[-1]
        nome_arquivo = f"{uuid4().hex[:8]}{extensao}"
        destino = self._resource_path("imagens", "familias", nome_arquivo)
        os.makedirs(os.path.dirname(destino), exist_ok=True)
        self._optimize_image(caminho_foto, destino)
        self._generate_thumb(destino)

        nova_familia = {
            "id": novo_id,
            "numero": numero,
            "nome": nome,
            "foto": os.path.join("imagens", "familias", nome_arquivo).replace("\\", "/"),
            "sorteado": False
        }

        familias.append(nova_familia)
        return self.salvar_familias(familias)

    def editar_familia(self, numero, novo_nome=None, nova_foto_path=None):
        familias = self.carregar_familias()
        familia = next((f for f in familias if str(f.get("numero")) == str(numero)), None)
        if not familia:
            return False
        if novo_nome is not None:
            nn = novo_nome.strip()
            if not nn:
                return False
            familia["nome"] = nn
        if nova_foto_path:
            if not os.path.exists(nova_foto_path) or not self._valid_image_ext(nova_foto_path):
                return False
            extensao = os.path.splitext(nova_foto_path)[-1]
            nome_arquivo = f"{uuid4().hex[:8]}{extensao}"
            destino = self._resource_path("imagens", "familias", nome_arquivo)
            os.makedirs(os.path.dirname(destino), exist_ok=True)
            self._optimize_image(nova_foto_path, destino)
            self._generate_thumb(destino)
            novo_rel = os.path.join("imagens", "familias", nome_arquivo).replace("\\", "/")
            old_rel = familia.get("foto")
            familia["foto"] = novo_rel
            if old_rel and old_rel != novo_rel:
                old_abs = self._resolve_photo_abs(old_rel)
                outros = [f for f in familias if f is not familia and f.get("foto") == old_rel]
                if not outros and os.path.exists(old_abs):
                    try:
                        os.remove(old_abs)
                    except Exception:
                        pass
                # remover thumb antiga
                try:
                    old_thumb = os.path.join(self.base_path_data, self._thumb_path(old_rel))
                    if os.path.exists(old_thumb):
                        os.remove(old_thumb)
                except Exception:
                    pass
        return self.salvar_familias(familias)

    def excluir_familia(self, numero):
        familias = self.carregar_familias()
        alvo = next((f for f in familias if str(f.get("numero")) == str(numero)), None)
        if not alvo:
            return False
        foto_rel = alvo.get("foto")
        familias = [f for f in familias if f is not alvo]
        ok = self.salvar_familias(familias)
        if ok and foto_rel:
            foto_abs = self._resolve_photo_abs(foto_rel)
            if os.path.exists(foto_abs):
                try:
                    os.remove(foto_abs)
                except Exception:
                    pass
            try:
                old_thumb = os.path.join(self.base_path_data, self._thumb_path(foto_rel))
                if os.path.exists(old_thumb):
                    os.remove(old_thumb)
            except Exception:
                pass
        return ok

    def _optimize_image(self, src_path, dst_path):
        try:
            from PySide6.QtGui import QImage
            img = QImage(src_path)
            if img.isNull():
                shutil.copy2(src_path, dst_path)
                return
            max_w, max_h = 1600, 1600
            w, h = img.width(), img.height()
            scale = min(max_w / max(w, 1), max_h / max(h, 1), 1.0)
            if scale < 1.0:
                img = img.scaled(int(w * scale), int(h * scale))
            fmt = "JPG" if dst_path.lower().endswith(('.jpg', '.jpeg')) else "PNG"
            quality = 85 if fmt == "JPG" else -1
            img.save(dst_path, fmt, quality)
        except Exception:
            try:
                shutil.copy2(src_path, dst_path)
            except Exception:
                pass

    def _thumb_path(self, foto_rel):
        base = os.path.basename(foto_rel)
        name, ext = os.path.splitext(base)
        return os.path.join("imagens", "thumbs", f"{name}_thumb.jpg").replace("\\", "/")

    def _generate_thumb(self, foto_abs):
        try:
            from PySide6.QtGui import QImage
            img = QImage(foto_abs)
            if img.isNull():
                return
            img = img.scaled(240, 240, aspectRatioMode=1)
            thumb_abs = os.path.join(self.base_path, "imagens", "thumbs", f"{os.path.splitext(os.path.basename(foto_abs))[0]}_thumb.jpg")
            img.save(thumb_abs, "JPG", 80)
        except Exception:
            pass

    def _is_valid_nome(self, nome):
        return isinstance(nome, str) and nome.strip() != ""

    def _is_valid_foto(self, foto):
        if not isinstance(foto, str) or foto.strip() == "":
            return False
        rel = foto.replace("\\", "/")
        ext = os.path.splitext(rel)[-1].lower()
        return rel.startswith("imagens/") and ext in {".png", ".jpg", ".jpeg"}

    def _is_valid_data(self, data_str):
        if not isinstance(data_str, str):
            return False
        return re.fullmatch(r"\d{2}/\d{2}/\d{4}", data_str) is not None

    def verificar_integridade_dados(self):
        try:
            familias = []
            if os.path.exists(self.familias_file):
                with open(self.familias_file, "r", encoding="utf-8") as f:
                    familias = json.load(f)
            else:
                self._atomic_write(self.familias_file, [])
                self._familias_cache = []
                return True
        except Exception as e:
            try:
                bak = self.familias_file + ".bak"
                if os.path.exists(self.familias_file):
                    shutil.copy2(self.familias_file, bak)
                self._atomic_write(self.familias_file, [])
                self._familias_cache = []
            except Exception:
                pass
            logging.error(f"Falha ao ler famílias, fallback para lista vazia: {str(e)}")
            return False

        corrigidas = []
        for f in familias:
            nome = f.get("nome")
            numero = f.get("numero")
            sorteado = f.get("sorteado", False)
            foto = f.get("foto", "")
            data_s = f.get("data_sorteio", None)
            try:
                numero = int(numero)
            except Exception:
                numero = None
            if not self._is_valid_nome(nome) or numero is None:
                logging.warning("Registro de família inválido removido")
                continue
            if not self._is_valid_foto(foto):
                foto = ""
            if data_s is not None and not self._is_valid_data(data_s):
                data_s = None
            sorteado = bool(sorteado)
            id_val = f.get("id")
            try:
                id_val = int(id_val) if id_val is not None else None
            except Exception:
                id_val = None
            nf = {
                "id": id_val if id_val is not None else numero,
                "numero": numero,
                "nome": str(nome).strip(),
                "foto": foto.replace("\\", "/") if foto else "",
                "sorteado": sorteado,
            }
            if data_s:
                nf["data_sorteio"] = data_s
            corrigidas.append(self._normalize_familia(nf))

        try:
            self._atomic_write(self.familias_file, corrigidas)
            self._familias_cache = corrigidas
            for nf in corrigidas:
                rel = nf.get("foto")
                if rel:
                    absf = self._resolve_photo_abs(rel)
                    if os.path.exists(absf):
                        self._generate_thumb(absf)
            logging.info(f"Validação: {len(corrigidas)} famílias válidas salvas")
            return True
        except Exception as e:
            logging.error(f"Erro ao salvar famílias após validação: {str(e)}")
            return False

    def verificar_integridade_sorteio(self):
        try:
            if not os.path.exists(self.sorteio_file):
                return True
            with open(self.sorteio_file, "r", encoding="utf-8") as f:
                dados = json.load(f)
            num = dados.get("ultimo_sorteado")
            try:
                num = int(num)
            except Exception:
                num = None
            familias = self.carregar_familias()
            ok = num is not None and any(int(f.get("numero")) == num and f.get("sorteado") for f in familias)
            if not ok:
                self._recalcular_ultimo_sorteado()
            return True
        except Exception as e:
            logging.error(f"Erro ao validar sorteio: {str(e)}")
            return False

    def executar_validacao_inicial(self):
        a = self.verificar_integridade_dados()
        b = self.verificar_integridade_sorteio()
        return a and b

    def alterar_status_familia(self, numero, novo_status: bool):
        try:
            familias = self.carregar_familias()
            familia = next((f for f in familias if str(f.get("numero")) == str(numero)), None)
            if not familia:
                return False
            familia["sorteado"] = bool(novo_status)
            if familia["sorteado"]:
                from datetime import datetime
                familia["data_sorteio"] = datetime.now().strftime("%d/%m/%Y")
                self.salvar_sorteio(numero)
            else:
                familia.pop("data_sorteio", None)
            ok = self.salvar_familias(familias)
            if ok:
                logging.info(f"Status da família {familia.get('nome')} ({numero}) alterado para {familia['sorteado']}")
                if not familia["sorteado"]:
                    # Se a família que estava como última for revertida, recalcula a última válida
                    self._recalcular_ultimo_sorteado()
            return ok
        except Exception as e:
            logging.error(f"Erro ao alterar status da família {numero}: {str(e)}")
            return False

    def _recalcular_ultimo_sorteado(self):
        """Determina e persiste a última família sorteada válida baseada na data_sorteio."""
        try:
            familias = self.carregar_familias(force_reload=True)
            # Filtra apenas sorteadas; usa data_sorteio como prioridade; em fallback usa número maior
            def key_fn(f):
                ds = f.get("data_sorteio")
                if ds:
                    try:
                        # dd/mm/yyyy -> tuple (yyyy, mm, dd) para ordenar corretamente
                        d, m, y = ds.split("/")
                        return (int(y), int(m), int(d), int(f.get("numero", 0)))
                    except Exception:
                        pass
                return (0, 0, 0, int(f.get("numero", 0)))
            sorteadas = [f for f in familias if f.get("sorteado")]
            if not sorteadas:
                # limpa arquivo e cache
                if os.path.exists(self.sorteio_file):
                    try:
                        os.remove(self.sorteio_file)
                    except Exception:
                        pass
                self._ultimo_sorteio_cache = None
                return None
            ultima = sorted(sorteadas, key=key_fn, reverse=True)[0]
            num = ultima.get("numero")
            self.salvar_sorteio(num)
            return num
        except Exception as e:
            logging.error(f"Erro ao recalcular último sorteado: {str(e)}")
            return None
