import os
import shutil
import tempfile
import unittest
from PySide6.QtWidgets import QApplication
from PySide6.QtGui import QImage
from src.data_manager import DataManager
from src.sorteio_tela import JanelaSorteio

app = QApplication.instance() or QApplication([])

class TestFlow(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.mkdtemp()
        self.dm = DataManager(base_path_override=self.tmp)
        os.makedirs(os.path.join(self.tmp, 'dados'), exist_ok=True)
        os.makedirs(os.path.join(self.tmp, 'imagens', 'familias'), exist_ok=True)
        img_path = os.path.join(self.tmp, 'imagens', 'familias', 'a.jpg')
        img = QImage(800, 600, QImage.Format_RGB32)
        img.fill(0xFF112233)
        img.save(img_path, 'JPG', 85)
        with open(self.dm.familias_file, 'w', encoding='utf-8') as f:
            import json
            json.dump([{"id":1,"numero":1,"nome":"Família A","foto":"imagens/familias/a.jpg"}], f)

    def tearDown(self):
        shutil.rmtree(self.tmp, ignore_errors=True)

    def test_sorteio_sem_campo_input(self):
        tela = JanelaSorteio("1")
        inputs = tela.findChildren(type(app.focusWidget()))
        self.assertTrue(all(i.__class__.__name__ != 'QLineEdit' for i in inputs))

    def test_mostrar_familia_por_numero(self):
        captured = []
        tela = JanelaSorteio("1")
        tela.sorteioRealizado.connect(lambda n: captured.append(n))
        app.processEvents()
        self.assertIn("1", captured)

if __name__ == "__main__":
    unittest.main()
