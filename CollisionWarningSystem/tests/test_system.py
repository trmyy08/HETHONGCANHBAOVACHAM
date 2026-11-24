import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from config import LEVEL_SAFE, LEVEL_WARNING, LEVEL_DANGER
from inference_engine import tinh_khoang_cach_an_toan, tinh_ttc, suy_dien
from sensor_simulator import DANH_SACH_KICH_BAN, ca_bien_kich_ban, sinh_du_lieu


class TestCollisionWarningSystem(unittest.TestCase):
    def test_safe_distance_increases_with_speed(self):
        d_slow = tinh_khoang_cach_an_toan(10 / 3.6, 0.8, 1.2)
        d_fast = tinh_khoang_cach_an_toan(80 / 3.6, 0.8, 1.2)
        self.assertGreater(d_fast, d_slow)

    def test_ttc_non_approaching_is_infinite(self):
        self.assertEqual(tinh_ttc(20, 0), float("inf"))
        self.assertEqual(tinh_ttc(20, -2), float("inf"))

    def test_sensor_failure_is_not_reported_as_safe(self):
        sample = {
            "t": 0.0, "khoang_cach": 40.0, "toc_do_xe_kmh": 50.0,
            "toc_do_vat_the_kmh": 0.0, "tinh_trang_duong": "kho",
            "trang_thai_tai_xe": "binh_thuong", "loai_vat_the": "xe_phia_truoc",
            "cam_bien_hoat_dong": False, "gia_toc_tuong_doi": 0.0,
            "da_va_cham": False,
        }
        result = suy_dien(sample)
        self.assertEqual(result["muc_canh_bao"], LEVEL_WARNING)

    def test_inference_trace_has_explanatory_evidence_summary(self):
        sample = {
            "t": 0.0, "khoang_cach": 5.0, "toc_do_xe_kmh": 60.0,
            "toc_do_vat_the_kmh": 0.0, "tinh_trang_duong": "kho",
            "trang_thai_tai_xe": "binh_thuong", "loai_vat_the": "xe_phia_truoc",
            "cam_bien_hoat_dong": True, "gia_toc_tuong_doi": 0.0,
            "da_va_cham": False,
        }
        result = suy_dien(sample)
        self.assertEqual(result["muc_canh_bao"], LEVEL_DANGER)
        self.assertTrue(result["working_memory"].get("co_bang_chung_nguy_hiem"))
        trace = result["trace_suy_dien_tien"]
        self.assertTrue(any(step.startswith(("M01:", "M02:", "M03:")) for step in trace))
        self.assertFalse(any(step.startswith(("M04:", "M05:", "M06:")) for step in trace))

    def test_seeded_sensor_data_is_reproducible(self):
        scenario = ca_bien_kich_ban(DANH_SACH_KICH_BAN[0], "051206001878")
        first = sinh_du_lieu(scenario, "051206001878", co_nhieu=True)
        second = sinh_du_lieu(scenario, "051206001878", co_nhieu=True)
        self.assertEqual(first, second)


if __name__ == "__main__":
    unittest.main(verbosity=2)
