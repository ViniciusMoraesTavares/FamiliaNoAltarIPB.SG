import os
import shutil
import tempfile
import time
import unittest
from PySide6.QtGui import QImage
from src.data_manager import DataManager

class TestPerformance(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.mkdtemp()
        self.dm = DataManager(base_path_override=self.tmp)
        os.makedirs(os.path.join(self.tmp, 'dados'), exist_ok=True)
        os.makedirs(os.path.join(self.tmp, 'imagens', 'familias'), exist_ok=True)

    def tearDown(self):
        shutil.rmtree(self.tmp, ignore_errors=True)

    def _make_image(self, path, w=2000, h=2000):
        img = QImage(w, h, QImage.Format_RGB32)
        img.fill(0xFF336699)
        img.save(path, 'PNG')

    def test_add_many_images_performance(self):
        count = 50
        srcs = []
        for i in range(count):
            p = os.path.join(self.tmp, f'src_{i}.png')
            self._make_image(p)
            srcs.append(p)
        t0 = time.perf_counter()
        for i, p in enumerate(srcs):
            self.dm.adicionar_familia(f'Fam {i}', p)
        t1 = time.perf_counter()
        elapsed = t1 - t0
        self.assertLess(elapsed, 10)

if __name__ == '__main__':
    unittest.main()
