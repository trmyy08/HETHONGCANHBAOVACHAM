const $ = (id) => document.getElementById(id);
let meta = null;
let lastSeries = [];
let lastDeadline = null;

const fmt = (value, suffix = "") =>
  value === null || value === undefined || !Number.isFinite(Number(value))
    ? "—"
    : Number(value).toFixed(2) + suffix;

function levelClass(level) {
  return level === "NGUY HIEM" ? "danger" : level === "CANH BAO" ? "warning" : "safe";
}
function levelText(level) {
  return level === "NGUY HIEM" ? "NGUY HIỂM" : level === "CANH BAO" ? "CẢNH BÁO" : "AN TOÀN";
}
async function api(url, options) {
  const response = await fetch(url, options);
  const data = await response.json();
  if (!response.ok) throw new Error(data.detail || "Lỗi API");
  return data;
}


async function loadMeta() {
  try {
    const [health, details, rules] = await Promise.all([
      api("/api/health"), api("/api/meta"), api("/api/rules"),
    ]);
    meta = details;
    $("backend").textContent = "ĐANG HOẠT ĐỘNG";
    $("ruleCount").textContent = health.rules;
    $("scenarioCount").textContent = health.scenarios;
    $("studentCount").textContent = health.students;
    $("sideStatus").textContent = "Đã kết nối";
    $("scenario").innerHTML = details.scenarios
      .map((item) => `<option value="${item.id}">${item.id} · ${item.name}</option>`)
      .join("");
    $("mssv").innerHTML = details.mssv.map((id) => `<option>${id}</option>`).join("");
    $("scenario").onchange = updateDescription;
    updateDescription();
    $("ruleRows").innerHTML = rules.map((rule) => `
      <tr>
        <td><b>${rule.id}</b></td>
        <td>${rule.group}</td>
        <td>${rule.priority}</td>
        <td>${Number(rule.confidence).toFixed(2)}</td>
        <td><span class="level ${levelClass(rule.conclusion)}">${levelText(rule.conclusion)}</span></td>
      </tr>`).join("");
  } catch (error) {
    $("backend").textContent = "MẤT KẾT NỐI";
    $("sideStatus").textContent = "Không kết nối";
    $("simMessage").textContent = `Không thể kết nối máy chủ: ${error.message}`;
  }
}
function updateDescription() {
  if (!meta) return;
  const selected = meta.scenarios.find((item) => item.id === $("scenario").value);
  if (selected) $("scenarioDesc").textContent = selected.description;
}

async function runSimulation() {
  const button = $("runSim");
  button.disabled = true;
  button.textContent = "Đang chạy…";
  $("simMessage").textContent = "Python đang tạo dữ liệu cảm biến và xử lý toàn bộ mẫu mô phỏng…";
  try {
    const result = await api("/api/simulate", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ scenario: $("scenario").value, mssv: $("mssv").value }),
    });
    $("simMetrics").hidden = false;
    $("mSamples").textContent = result.samples.toLocaleString("vi-VN");
    $("mWarning").textContent = fmt(result.first_warning, " giây");
    $("mEarly").textContent = fmt(result.early_warning, " giây");
    $("mConflict").textContent = result.conflicts.toLocaleString("vi-VN");
    const collisionText = result.collision ? "Có va chạm trong mô phỏng" : "Không ghi nhận va chạm trong mô phỏng";
    $("simMessage").textContent = `${result.scenario} · ${result.scenario_name} · MSSV ${result.mssv} · ${collisionText}`;
    lastSeries = result.series;
    lastDeadline = result.deadline;
    drawChart(result.series, result.deadline);
  } catch (error) {
    $("simMessage").textContent = `Lỗi mô phỏng: ${error.message}`;
  } finally {
    button.disabled = false;
    button.textContent = "▶ Chạy mô phỏng";
  }
}

function drawChart(rows, deadline = null) {
  const canvas = $("simChart");
  const context = canvas.getContext("2d");
  const width = canvas.clientWidth;
  const height = 220;
  const ratio = window.devicePixelRatio || 1;
  canvas.width = width * ratio;
  canvas.height = height * ratio;
  context.scale(ratio, ratio);
  context.clearRect(0, 0, width, height);
  if (!rows.length) return;

  const maxTime = rows[rows.length - 1].t || 1;
  const maxDistance = Math.max(10, ...rows.map((row) => row.distance));
  const left = 44, right = 14, top = 14, bottom = 30;
  const plotWidth = width - left - right, plotHeight = height - top - bottom;
  const xFor = (time) => left + plotWidth * time / maxTime;
  const yFor = (distance) => top + plotHeight * (1 - distance / maxDistance);

  context.font = "11px Arial";
  context.strokeStyle = "#edf1f6";
  context.fillStyle = "#8795a8";
  context.lineWidth = 1;
  for (let index = 0; index <= 4; index++) {
    const y = top + plotHeight * index / 4;
    context.beginPath(); context.moveTo(left, y); context.lineTo(width - right, y); context.stroke();
    context.fillText(`${(maxDistance * (1 - index / 4)).toFixed(0)} m`, 2, y + 4);
  }
  for (let index = 0; index <= 5; index++) {
    const x = left + plotWidth * index / 5;
    context.fillText(`${(maxTime * index / 5).toFixed(1)} s`, x - 12, height - 9);
  }

  // Deadline: vertical reference marker from the simulation's calculated threshold.
  if (deadline !== null && deadline !== undefined && Number.isFinite(Number(deadline)) && deadline >= 0 && deadline <= maxTime) {
    const deadlineX = xFor(deadline);
    context.save();
    context.setLineDash([5, 4]);
    context.strokeStyle = "#9a6471";
    context.lineWidth = 1.5;
    context.beginPath(); context.moveTo(deadlineX, top); context.lineTo(deadlineX, top + plotHeight); context.stroke();
    context.setLineDash([]);
    context.fillStyle = "#9a6471";
    context.fillText(`Mốc tới hạn ${deadline.toFixed(2)} s`, Math.min(deadlineX + 5, width - 120), top + 12);
    context.restore();
  }

  context.beginPath();
  rows.forEach((row, index) => index ? context.lineTo(xFor(row.t), yFor(row.distance)) : context.moveTo(xFor(row.t), yFor(row.distance)));
  context.strokeStyle = "#3978e8";
  context.lineWidth = 2.3;
  context.stroke();
  rows.forEach((row) => {
    if (row.level !== "NGUY HIEM" && row.level !== "CANH BAO") return;
    context.beginPath(); context.arc(xFor(row.t), yFor(row.distance), 2.5, 0, Math.PI * 2);
    context.fillStyle = row.level === "NGUY HIEM" ? "#e65f62" : "#e5a43d";
    context.fill();
  });
}
async function runInference() {
  const payload = {
    distance: Number($("distance").value),
    ego_speed: Number($("ego").value),
    object_speed: Number($("objectSpeed").value),
    relative_acceleration: Number($("relativeAcceleration").value),
    road: $("road").value,
    driver: $("driver").value,
    object_type: $("objectType").value,
    sensor_ok: true,
  };
  try {
    const result = await api("/api/infer", {
      method: "POST", headers: { "Content-Type": "application/json" }, body: JSON.stringify(payload),
    });
    const className = levelClass(result.level);
    $("inferResult").className = `result-card ${className}`;
    $("inferResult").innerHTML = `
      <h3>${levelText(result.level)}</h3><p>${result.action}</p>
      <div class="result-kpis">
        <div><small>Luật thắng</small><b>${result.winning_rule}</b></div>
        <div><small>Độ tin cậy</small><b>${fmt(result.confidence * 100, "%")}</b></div>
        <div><small>Thời gian đến va chạm (TTC)</small><b>${fmt(result.ttc, " giây")}</b></div>
        <div><small>Khoảng cách an toàn</small><b>${fmt(result.safe_distance, " m")}</b></div>
        <div><small>Số luật khớp</small><b>${result.matched_rules}</b></div>
      </div>`;
    $("explain").hidden = false;
    const traceItems = result.trace.map((line) => `<li>${line}</li>`).join("");
    const ruleRows = result.explanation.map((rule) => `
      <tr>
        <td>${rule.ma_luat}</td><td>${rule.group_display}</td><td>${levelText(rule.ket_luan)}</td>
        <td>${rule.uu_tien}</td><td>${rule.la_luat_thang ? "★ Luật thắng" : "Luật khớp"}</td>
        <td>${rule.explanation_display}</td>
      </tr>`).join("");
    $("explain").innerHTML = `
      <h3>Trace giải thích quá trình xử lý</h3>
      <ol>${traceItems}</ol>
      <p class="trace-note">${result.trace_note}</p>
      <h3>Các luật được kích hoạt</h3>
      <div class="table-scroll"><table>
        <thead><tr><th>Luật</th><th>Nhóm</th><th>Kết luận</th><th>Ưu tiên</th><th>Trạng thái</th><th>Giải thích</th></tr></thead>
        <tbody>${ruleRows}</tbody>
      </table></div>`;
  } catch (error) {
    $("inferResult").className = "result-placeholder";
    $("inferResult").textContent = `Không thể thực hiện suy luận: ${error.message}`;
  }
}

// Sidebar page navigation: each feature is shown as its own page view.
const pageIds = ["overview", "simulation", "inference", "rules"];
function showPage(pageId, updateHash = true) {
  const target = pageIds.includes(pageId) ? pageId : "overview";
  document.querySelectorAll(".page-view").forEach((page) => {
    page.hidden = page.id !== target;
  });
  document.querySelectorAll(".sidebar nav a[data-page]").forEach((link) => {
    const isActive = link.dataset.page === target;
    link.classList.toggle("active", isActive);
    if (isActive) link.setAttribute("aria-current", "page");
    else link.removeAttribute("aria-current");
  });
  if (updateHash && window.location.hash !== `#${target}`) {
    history.pushState(null, "", `#${target}`);
  }
  window.scrollTo({ top: 0, behavior: "smooth" });
}
function routeFromHash() {
  showPage(window.location.hash.slice(1) || "overview", false);
}
document.querySelectorAll(".sidebar nav a[data-page]").forEach((link) => {
  link.addEventListener("click", (event) => {
    event.preventDefault();
    showPage(link.dataset.page);
  });
});
window.addEventListener("hashchange", routeFromHash);
window.addEventListener("popstate", routeFromHash);
routeFromHash();

$("clock").textContent = new Date().toLocaleDateString("vi-VN", { weekday: "short", day: "2-digit", month: "short", year: "numeric" });
loadMeta();
window.addEventListener("resize", () => { if (lastSeries.length) drawChart(lastSeries, lastDeadline); });
