import shutil
import tempfile
import unittest
from pathlib import Path

import SimpleITK as sitk
import numpy as np

import Functions.EXE as exe_dir
from Functions.Python.uncertainty_features import ncmi, generate_config_file


class NcmiTester(unittest.TestCase):
    root_dir: Path

    @classmethod
    def setUpClass(cls) -> None:
        cls.root_dir = Path(tempfile.mkdtemp())

    @classmethod
    def tearDownClass(cls) -> None:
        pass
        shutil.rmtree(cls.root_dir)

    def test_ncmi_sample(self):
        # ToDO not functional
        ncmi_executable = Path(exe_dir.__file__).parent / "NCMI.exe"
        image_paths = []
        shapes = (100, 100, 50)
        for i in range(2):
            im_sitk = sitk.GetImageFromArray(np.random.randint(-1000, 1000, shapes, dtype=np.int16))
            im_path = self.root_dir / f"im{i}.mha"
            sitk.WriteImage(im_sitk, str(im_path))
            image_paths.append(im_path)

        mask_im = np.zeros(shapes, dtype=np.int8)
        m = 40
        mask_im[m: shapes[0]-10, m: shapes[1]-10, m: shapes[2]-10] = 1
        mask_sitk = sitk.GetImageFromArray(mask_im)
        mask_path = self.root_dir / "mask.mha"
        sitk.WriteImage(mask_sitk, str(mask_path))
        config_path = self.root_dir / "config.txt"
        generate_config_file(config_path=config_path,
                             image_paths=[p for p in image_paths],
                             mask_path=mask_path,
                             output_dir=self.root_dir,
                             min_boxsize=5,
                             max_boxsize=40)

        ncmi(None, ncmi_executable=str(ncmi_executable), config_file=str(config_path), pool_dir=str(self.root_dir),
             pooled_name="pooled_NCMI_r0.bin")


if __name__ == '__main__':
    unittest.main()
