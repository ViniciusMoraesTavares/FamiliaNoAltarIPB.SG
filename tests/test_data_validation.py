import os
import shutil
import tempfile
import unittest
from src.data_manager import DataManager

class TestDataValidation(unittest.TestCase):
    def setUp(self):
        DataManager._instance = None
        DataManager._familias_cache = None
        DataManager._ultimo_sorteio_cache = None
        self.tmp = tempfile.mkdtemp()
        self.dm = DataManager(base_path_override=self.tmp)
        os.makedirs(os.path.join(self.tmp, 'dados'), exist_ok=True)
        os.makedirs(os.path.join(self.tmp, 'imagens', 'familias'), exist_ok=True)

    def tearDown(self):
        DataManager._instance = None
        DataManager._familias_cache = None
        DataManager._ultimo_sorteio_cache = None
        shutil.rmtree(self.tmp, ignore_errors=True)

    def write_familias(self, data):
        with open(self.dm.familias_file, 'w', encoding='utf-8') as f:
            f.write(data)

    def test_invalid_json_fallback(self):
        self.write_familias('[ invalid')
        ok = self.dm.verificar_integridade_dados()
        self.assertFalse(ok)
        familias = self.dm.carregar_familias(force_reload=True)
        self.assertEqual(familias, [])

    def test_valid_family_normalization(self):
        familias = [
            {"id": 1, "numero": "1", "nome": "Família A", "foto": "imagens/familias/a.jpg", "sorteado": False},
            {"id": 2, "numero": 2, "nome": "  Família B  ", "foto": os.path.join(self.tmp, 'imagens', 'familias', 'b.png'), "sorteado": True, "data_sorteio": "12/12/2024"},
        ]
        with open(self.dm.familias_file, 'w', encoding='utf-8') as f:
            import json
            json.dump(familias, f)
        ok = self.dm.verificar_integridade_dados()
        self.assertTrue(ok)
        res = self.dm.carregar_familias(force_reload=True)
        self.assertEqual(res[0]['numero'], 1)
        self.assertTrue(res[1]['foto'].startswith('imagens/familias/'))
        self.assertEqual(res[1]['data_sorteio'], '12/12/2024')

    def test_remove_invalid_family(self):
        familias = [
            {"id": 1, "numero": "not-int", "nome": "X", "foto": "imagens/familias/x.jpg"},
            {"id": 2, "numero": 2, "nome": "", "foto": "imagens/familias/y.jpg"},
            {"id": 3, "numero": 3, "nome": "OK", "foto": "imagens/familias/z.gif"},
        ]
        with open(self.dm.familias_file, 'w', encoding='utf-8') as f:
            import json
            json.dump(familias, f)
        self.dm.verificar_integridade_dados()
        res = self.dm.carregar_familias(force_reload=True)
        self.assertEqual(len(res), 1)
        self.assertEqual(res[0]['nome'], 'OK')
        self.assertEqual(res[0]['foto'], '')

    def test_sorteio_integrity(self):
        with open(self.dm.familias_file, 'w', encoding='utf-8') as f:
            import json
            json.dump([
                {"id": 1, "numero": 1, "nome": "A", "foto": "imagens/familias/a.jpg"}
            ], f)
        with open(self.dm.sorteio_file, 'w', encoding='utf-8') as f:
            import json
            json.dump({"ultimo_sorteado": "x"}, f)
        self.dm.verificar_integridade_dados()
        ok = self.dm.verificar_integridade_sorteio()
        self.assertTrue(ok)
        self.assertFalse(os.path.exists(self.dm.sorteio_file))

    def test_excluir_familia_remove_foto(self):
        foto_path = os.path.join(self.tmp, 'imagens', 'familias', 'a.jpg')
        with open(foto_path, 'wb') as f:
            f.write(b'\x00')
        familias = [{"id": 1, "numero": 1, "nome": "A", "foto": "imagens/familias/a.jpg"}]
        with open(self.dm.familias_file, 'w', encoding='utf-8') as f:
            import json
            json.dump(familias, f)
        self.dm.excluir_familia(1)
        self.assertFalse(os.path.exists(foto_path))

    def test_excluir_familia_renumera_do_inicio(self):
        familias = [
            {"id": 1, "numero": 1, "nome": "A", "foto": ""},
            {"id": 2, "numero": 2, "nome": "B", "foto": ""},
            {"id": 3, "numero": 3, "nome": "C", "foto": ""},
        ]
        with open(self.dm.familias_file, 'w', encoding='utf-8') as f:
            import json
            json.dump(familias, f)
        ok = self.dm.excluir_familia(1)
        self.assertTrue(ok)
        res = self.dm.carregar_familias(force_reload=True)
        self.assertEqual([f["numero"] for f in res], [1, 2])
        self.assertEqual([f["nome"] for f in res], ["B", "C"])

    def test_excluir_familia_renumera_do_meio(self):
        familias = [
            {"id": 1, "numero": 1, "nome": "A", "foto": ""},
            {"id": 2, "numero": 2, "nome": "B", "foto": ""},
            {"id": 3, "numero": 3, "nome": "C", "foto": ""},
            {"id": 4, "numero": 4, "nome": "D", "foto": ""},
        ]
        with open(self.dm.familias_file, 'w', encoding='utf-8') as f:
            import json
            json.dump(familias, f)
        ok = self.dm.excluir_familia(3)
        self.assertTrue(ok)
        res = self.dm.carregar_familias(force_reload=True)
        self.assertEqual([f["numero"] for f in res], [1, 2, 3])
        self.assertEqual([f["nome"] for f in res], ["A", "B", "D"])

    def test_excluir_familia_renumera_do_fim(self):
        familias = [
            {"id": 1, "numero": 1, "nome": "A", "foto": ""},
            {"id": 2, "numero": 2, "nome": "B", "foto": ""},
            {"id": 3, "numero": 3, "nome": "C", "foto": ""},
        ]
        with open(self.dm.familias_file, 'w', encoding='utf-8') as f:
            import json
            json.dump(familias, f)
        ok = self.dm.excluir_familia(3)
        self.assertTrue(ok)
        res = self.dm.carregar_familias(force_reload=True)
        self.assertEqual([f["numero"] for f in res], [1, 2])
        self.assertEqual([f["nome"] for f in res], ["A", "B"])

    def test_excluir_familia_inexistente_retorna_false(self):
        familias = [
            {"id": 1, "numero": 1, "nome": "A", "foto": ""},
            {"id": 2, "numero": 2, "nome": "B", "foto": ""},
        ]
        with open(self.dm.familias_file, 'w', encoding='utf-8') as f:
            import json
            json.dump(familias, f)
        ok = self.dm.excluir_familia(99)
        self.assertFalse(ok)

    def test_excluir_familia_recalcula_ultimo_sorteado_apos_renumeracao(self):
        familias = [
            {"id": 1, "numero": 1, "nome": "A", "foto": "", "sorteado": False},
            {"id": 2, "numero": 2, "nome": "B", "foto": "", "sorteado": True, "data_sorteio": "01/01/2026"},
            {"id": 3, "numero": 3, "nome": "C", "foto": "", "sorteado": True, "data_sorteio": "02/01/2026"},
        ]
        with open(self.dm.familias_file, 'w', encoding='utf-8') as f:
            import json
            json.dump(familias, f)
        self.dm.salvar_sorteio(3)
        ok = self.dm.excluir_familia(1)
        self.assertTrue(ok)
        ultimo = self.dm.carregar_ultimo_sorteio(force_reload=True)
        self.assertEqual(int(ultimo), 2)

    def test_editar_familia_troca_foto(self):
        old_path = os.path.join(self.tmp, 'imagens', 'familias', 'old.jpg')
        with open(old_path, 'wb') as f:
            f.write(b'\x00')
        familias = [{"id": 1, "numero": 1, "nome": "A", "foto": "imagens/familias/old.jpg"}]
        with open(self.dm.familias_file, 'w', encoding='utf-8') as f:
            import json
            json.dump(familias, f)
        new_path = os.path.join(self.tmp, 'imagens', 'familias', 'new.png')
        with open(new_path, 'wb') as f:
            f.write(b'\x00')
        ok = self.dm.editar_familia(1, "B", new_path)
        self.assertTrue(ok)
        self.assertFalse(os.path.exists(old_path))

if __name__ == '__main__':
    unittest.main()
