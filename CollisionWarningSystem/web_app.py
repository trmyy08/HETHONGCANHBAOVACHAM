"""FastAPI adapter for the original De tai 36 v2.0 AI simulation core."""
from pathlib import Path
import math
import sys
from typing import Optional

from fastapi import FastAPI, HTTPException
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel, Field


ROOT = Path(__file__).resolve().parent
SRC = ROOT / "src"
sys.path.insert(0, str(SRC))

from config import MSSV_LIST, LEVEL_SAFE, LEVEL_WARNING, LEVEL_DANGER  # noqa: E402
from knowledge_base import RULE_BASE, thong_ke_co_so_luat  # noqa: E402
from sensor_simulator import DANH_SACH_KICH_BAN  # noqa: E402
from inference_engine import suy_dien  # noqa: E402
from experiment import chay_mot_kich_ban  # noqa: E402


app = FastAPI(title="Hệ thống cảnh báo va chạm – Đề tài 36", version="2.0-web")
app.mount("/static", StaticFiles(directory=str(ROOT / "web")), name="static")



class InferInput(BaseModel):
    distance: float = Field(ge=0, le=1000, description="Khoảng cách (m)")
    ego_speed: float = Field(ge=0, le=300, description="Tốc độ xe chủ (km/h)")
    object_speed: float = Field(ge=0, le=300, description="Tốc độ vật thể (km/h)")
    relative_acceleration: float = Field(
        default=0.0, ge=-20, le=20, description="Gia tốc tiếp cận tương đối (m/s²)"
    )
    road: str = "kho"
    driver: str = "binh_thuong"
    object_type: str = "xe_phia_truoc"
    sensor_ok: bool = True


class SimInput(BaseModel):
    scenario: str = "KB1"
    mssv: Optional[str] = None



SCENARIO_DISPLAY = {
    "KB1": ("Đô thị – xe trước phanh gấp", "Di chuyển trong đô thị ở tốc độ khoảng 40 km/h, bám theo xe trước 30 m. Sau đó xe trước phanh gấp, mô phỏng tình huống va chạm liên hoàn thường gặp trong đô thị."),
    "KB2": ("Quốc lộ – tốc độ trung bình", "Chạy khoảng 70 km/h trên quốc lộ, cách xe tải phía trước 55 m. Xe tải giảm tốc khi đến khu dân cư."),
    "KB3": ("Cao tốc – vật cản đứng yên", "Chạy khoảng 100 km/h trên cao tốc, phía trước có vật cản đứng yên trong làn. Tốc độ tiếp cận lớn, cần đánh giá khả năng tránh va chạm."),
    "KB4": ("Trời mưa – đường ướt", "Di chuyển dưới trời mưa trên mặt đường ướt, độ bám giảm và quãng đường phanh tăng. Kiểm tra khả năng cảnh báo trong điều kiện bất lợi."),
    "KB5": ("Tài xế mất tập trung", "Xe chạy tốc độ cao, tài xế mất tập trung làm tăng thời gian phản ứng. Xe phía trước giảm tốc, kiểm tra khả năng cảnh báo sớm."),
    "KB6": ("Duy trì khoảng cách an toàn (đối chứng âm)", "Chạy 60 km/h, giữ đều khoảng cách 60 m với xe trước cùng tốc độ. Kịch bản này không có nguy cơ va chạm, dùng để kiểm tra hệ thống có báo động giả hay không."),
    "KB7": ("Người đi bộ băng qua đường", "Di chuyển trong đô thị, phía trước có người đi bộ băng qua đường. Đối tượng dễ bị tổn thương nên hệ thống áp dụng ngưỡng thận trọng."),
    "KB8": ("Xe cắt ngang tại giao lộ", "Tiếp cận giao lộ có xe cắt ngang phía trước. Tình huống mô phỏng quỹ đạo giao nhau và nguy cơ va chạm."),
}
GROUP_DISPLAY = {
    "Loc tinh huong": "Lọc tình huống",
    "Khoang cach tuyet doi": "Khoảng cách tuyệt đối",
    "Ket hop toc do - khoang cach": "Kết hợp tốc độ – khoảng cách",
    "Dieu kien moi truong": "Điều kiện môi trường",
    "Loai vat the": "Loại vật thể",
    "Xu huong": "Xu hướng tiếp cận",
    "Mac dinh": "Luật mặc định",
}
RULE_EXPLANATIONS = {
    "R01": "Cảm biến mất tín hiệu. Không đủ dữ liệu để kết luận an toàn nên phát cảnh báo trung gian.",
    "R02": "Không phát hiện vật thể trong phạm vi radar; không cần cảnh báo.",
    "R03": "Tốc độ xe rất thấp; bỏ qua cảnh báo khi xe gần như đứng yên.",
    "R04": "Khoảng cách nhỏ hơn giới hạn vật lý tối thiểu; nguy hiểm bất kể tốc độ.",
    "R05": "Thời gian đến va chạm (TTC) nằm dưới ngưỡng nguy hiểm.",
    "R06": "Khoảng cách thực tế nhỏ hơn 60% khoảng cách an toàn.",
    "R07": "Cả TTC và khoảng cách đều vi phạm tiêu chí an toàn; nguy cơ tăng cao.",
    "R08": "TTC nằm trong vùng cảnh báo.",
    "R09": "Khoảng cách nhỏ hơn mức an toàn nhưng chưa vào ngưỡng nguy hiểm.",
    "R10": "Độ bám đường thấp và TTC ngắn làm tăng nguy cơ phanh; nâng cảnh báo.",
    "R11": "Điều kiện mặt đường làm mở rộng vùng cảnh báo.",
    "R12": "Thời gian phản ứng của tài xế dài; cần cảnh báo sớm hơn.",
    "R13": "Tài xế mất tập trung và TTC ngắn; nguy cơ không còn đủ thời gian phản ứng.",
    "R14": "Vật cản đứng yên phía trước, cần ưu tiên xử lý nguy cơ.",
    "R15": "Người đi bộ trong quỹ đạo tiếp cận; áp dụng ngưỡng thận trọng.",
    "R16": "Xe cắt ngang có quỹ đạo giao nhau với xe chủ.",
    "R17": "Gia tốc tiếp cận tăng nhanh; TTC có thể rút ngắn nhanh chóng.",
    "R18": "Khoảng cách đang thu hẹp; cần theo dõi xu hướng.",
    "R19": "Vật thể không tiếp cận và khoảng cách đủ an toàn.",
    "R20": "TTC và khoảng cách đều vượt ngưỡng an toàn.",
    "R21": "Luật mặc định: không có luật cảnh báo nào phù hợp.",
    "R22": "TTC cực ngắn; va chạm gần như chắc chắn nếu không can thiệp ngay theo giả định mô phỏng.",
}
TRACE_NOTE = (
    "Các sự kiện M01–M03 chỉ tổng hợp bằng chứng từ những luật R01–R22 đã khớp, "
    "phục vụ giải thích. Chúng không tham gia chọn kết luận cuối. Kết luận được "
    "quyết định trực tiếp bởi luật tác nghiệp khớp thông qua cơ chế giải quyết "
    "xung đột theo độ ưu tiên, mức nghiêm trọng và độ tin cậy."
)


def display_trace(trace):
    lines = []
    for entry in trace:
        if entry.startswith(("M04:", "M05:", "M06:")):
            continue
        if entry.startswith("M01:"):
            lines.append("M01: Tổng hợp bằng chứng nguy hiểm từ các luật khớp.")
        elif entry.startswith("M02:"):
            lines.append("M02: Tổng hợp bằng chứng cảnh báo từ các luật khớp.")
        elif entry.startswith("M03:"):
            lines.append("M03: Tổng hợp bằng chứng an toàn từ các luật khớp.")
        elif entry.startswith("R") and ": dieu kien dung" in entry:
            rule_id = entry.split(":", 1)[0]
            lines.append(f"{rule_id}: Điều kiện luật thỏa mãn; đưa vào tập luật khớp.")
    return lines


@app.get("/")
def home():
    return FileResponse(ROOT / "web" / "index.html")



@app.get("/api/health")
def health():
    stats = thong_ke_co_so_luat()
    return {
        "status": "online",
        "project": "Đề tài 36 – Mô phỏng hệ thống cảnh báo va chạm",
        "version": "2.0",
        "rules": stats.get("tong_so_luat", len(RULE_BASE)),
        "scenarios": len(DANH_SACH_KICH_BAN),
        "students": len(MSSV_LIST),
        "engine": "Đối sánh luật + tổng hợp bằng chứng + giải quyết xung đột",
    }


@app.get("/api/meta")
def meta():
    return {
        "mssv": MSSV_LIST,
        "levels": [LEVEL_SAFE, LEVEL_WARNING, LEVEL_DANGER],
        "roads": ["kho", "am", "uot", "tron"],
        "drivers": ["tinh_tao", "binh_thuong", "met_moi", "mat_tap_trung"],
        "objects": ["xe_phia_truoc", "vat_can_tinh", "nguoi_di_bo", "xe_cat_ngang"],
        "scenarios": [
            {
                "id": scenario.ma,
                "name": SCENARIO_DISPLAY[scenario.ma][0],
                "description": SCENARIO_DISPLAY[scenario.ma][1],
                "ego_speed": scenario.toc_do_xe_kmh,
                "object_speed": scenario.toc_do_vat_the_kmh,
                "distance": scenario.khoang_cach_dau,
                "road": scenario.tinh_trang_duong,
                "driver": scenario.trang_thai_tai_xe,
            }
            for scenario in DANH_SACH_KICH_BAN
        ],
    }



def safe_number(value):
    if isinstance(value, float) and (math.isinf(value) or math.isnan(value)):
        return None
    return value



def public_result(result):
    return {
        "time": result["t"],
        "distance": result["khoang_cach"],
        "ego_speed": result["toc_do_xe_kmh"],
        "object_speed": result["toc_do_vat_the_kmh"],
        "ttc": safe_number(result["ttc"]),
        "safe_distance": round(result["khoang_cach_an_toan"], 2),
        "distance_ratio": round(result["ty_le_khoang_cach"], 3),
        "level": result["muc_canh_bao"],
        "winning_rule": result["luat_thang"],
        "confidence": result["do_tin_cay"],
        "action": {
            LEVEL_SAFE: "Giữ nguyên hành trình. Không phát cảnh báo.",
            LEVEL_WARNING: "Cảnh báo âm thanh ngắt quãng và đèn vàng. Tài xế nên nhả chân ga.",
            LEVEL_DANGER: "Cảnh báo âm thanh liên tục, đèn đỏ và rung vô lăng. Mô phỏng đề xuất hỗ trợ phanh khẩn cấp (AEB).",
        }.get(result["muc_canh_bao"], result["hanh_dong"]),
        "matched_rules": result["so_luat_khop"],
        "conflict": result["co_xung_dot"],
        "facts": result["facts"],
        "trace": display_trace(result["trace_suy_dien_tien"]),
        "trace_note": TRACE_NOTE,
        "explanation": [
            {
                **item,
                "group_display": GROUP_DISPLAY.get(item["nhom"], item["nhom"]),
                "explanation_display": RULE_EXPLANATIONS.get(item["ma_luat"], item["dien_giai"]),
            }
            for item in result["giai_trinh"]
        ],
    }



@app.post("/api/infer")
def infer(data: InferInput):
    sample = {
        "t": 0.0,
        "khoang_cach": data.distance,
        "toc_do_xe_kmh": data.ego_speed,
        "toc_do_vat_the_kmh": data.object_speed,
        "tinh_trang_duong": data.road,
        "trang_thai_tai_xe": data.driver,
        "loai_vat_the": data.object_type,
        "cam_bien_hoat_dong": data.sensor_ok,
        "gia_toc_tuong_doi": data.relative_acceleration,
    }
    try:
        return public_result(suy_dien(sample))
    except KeyError as error:
        raise HTTPException(422, f"Tham số không hợp lệ: {error}") from error



@app.post("/api/simulate")
def simulate(data: SimInput):
    scenario = next((item for item in DANH_SACH_KICH_BAN if item.ma == data.scenario), None)
    if scenario is None:
        raise HTTPException(404, "Không tìm thấy kịch bản")
    mssv = data.mssv or MSSV_LIST[0]
    if mssv not in MSSV_LIST:
        raise HTTPException(422, "MSSV không nằm trong danh sách cấu hình")
    result = chay_mot_kich_ban(scenario, mssv)
    rows = []
    stride = max(1, len(result["du_lieu"]) // 350)
    for index in range(0, len(result["du_lieu"]), stride):
        sample = result["du_lieu"][index]
        inference = result["ket_qua_suy_dien"][index]
        rows.append(
            {
                "t": sample["t"],
                "distance": sample["khoang_cach"],
                "ego_speed": sample["toc_do_xe_kmh"],
                "object_speed": sample["toc_do_vat_the_kmh"],
                "ttc": safe_number(inference["ttc"]),
                "level": inference["muc_canh_bao"],
                "rule": inference["luat_thang"],
            }
        )
    latest = public_result(result["ket_qua_suy_dien"][-1]) if result["ket_qua_suy_dien"] else None
    return {
        "scenario": scenario.ma,
        "scenario_name": SCENARIO_DISPLAY[scenario.ma][0],
        "mssv": mssv,
        "samples": len(result["du_lieu"]),
        "collision": result["co_va_cham"],
        "deadline": safe_number(result["t_toi_han"]),
        "first_warning": result["t_canh_bao_luat"],
        "first_danger": result["t_nguy_hiem_luat"],
        "early_warning": result["du_bao_truoc_luat"],
        "distribution": result["phan_bo_luat"],
        "conflicts": result["so_mau_xung_dot"],
        "average_matched_rules": result["so_luat_khop_tb"],
        "rules_used": result["cac_luat_da_dung"],
        "series": rows,
        "latest": latest,
    }



@app.get("/api/rules")
def rules():
    return [
        {
            "id": rule.id,
            "group": GROUP_DISPLAY.get(rule.nhom, rule.nhom),
            "priority": rule.uu_tien,
            "confidence": rule.do_tin_cay,
            "conclusion": rule.ket_luan,
            "explanation": RULE_EXPLANATIONS.get(rule.id, rule.giai_thich),
        }
        for rule in RULE_BASE
    ]
