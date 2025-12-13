import unittest
from PySide6.QtWidgets import QApplication
from src.sorteio_tela import JanelaSorteio

app = QApplication.instance() or QApplication([])

class TestSorteioOpen(unittest.TestCase):
    def test_abertura_sem_numero(self):
        tela = JanelaSorteio()
        app.processEvents()
        self.assertTrue(tela.isVisible())

    def test_sem_campo_numero_na_tela_sorteio(self):
        tela = JanelaSorteio()
        app.processEvents()
        children = tela.findChildren(type(app.focusWidget()))
        self.assertTrue(all(c.__class__.__name__ != 'QLineEdit' for c in children))

    def test_abertura_com_numero(self):
        tela = JanelaSorteio("1")
        app.processEvents()
        self.assertTrue(tela.isVisible())

if __name__ == "__main__":
    unittest.main()
