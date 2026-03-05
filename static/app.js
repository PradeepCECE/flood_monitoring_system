const $ = (id) => document.getElementById(id);

function setTheme(flags) {
  document.body.classList.remove('theme-normal', 'theme-rain', 'theme-flood');

  if (flags?.flood_alert_sent) {
    document.body.classList.add('theme-flood');
  } else if (flags?.rain_detected) {
    document.body.classList.add('theme-rain');
  } else {
    document.body.classList.add('theme-normal');
  }
}

function renderWeather(latest) {
  if (!latest) return;
  $('rainfallValue').textContent = `${Number(latest.rainfall_mm).toFixed(2)} mm`;
  $('temperatureValue').textContent = `${Number(latest.temperature_c).toFixed(1)} °C`;
  $('humidityValue').textContent = `${Number(latest.humidity_pct).toFixed(0)} %`;
  $('pressureValue').textContent = `${Number(latest.pressure_hpa).toFixed(0)} hPa`;
  $('windValue').textContent = `${Number(latest.wind_speed_ms).toFixed(1)} m/s`;
  $('cloudValue').textContent = `${Number(latest.cloud_coverage_pct).toFixed(0)} %`;
  $('timestampValue').textContent = new Date(latest.recorded_at).toLocaleString();

  const raining = Number(latest.rainfall_mm) > 0;
  $('statusText').textContent = raining
    ? 'Rain detected in the latest 3-hour weather block.'
    : 'No rain detected in the latest 3-hour weather block.';
}

function renderPrediction(prediction) {
  if (!prediction) {
    $('riskBadge').textContent = 'Waiting for 3 full days';
    $('probabilityValue').textContent = '0%';
    $('reasonText').textContent = 'The sliding window is not ready yet.';
    return;
  }

  $('riskBadge').textContent = `${prediction.risk_level} RISK`;
  $('probabilityValue').textContent = `${Math.round(Number(prediction.risk_probability) * 100)}%`;
  $('reasonText').textContent = prediction.reason;
}

function renderSummaryList(items) {
  const host = $('summaryList');
  host.innerHTML = '';

  if (!items?.length) {
    host.innerHTML = '<div class="list-item"><span>No daily summaries yet.</span></div>';
    return;
  }

  items.forEach((item) => {
    const div = document.createElement('div');
    div.className = 'list-item';
    div.innerHTML = `
      <strong>${item.day}</strong>
      <span>Rain: ${Number(item.total_rainfall_mm).toFixed(2)} mm<br>
      Humidity: ${Number(item.avg_humidity_pct).toFixed(1)} %<br>
      Temp: ${Number(item.avg_temperature_c).toFixed(1)} °C</span>
    `;
    host.appendChild(div);
  });
}

function renderAlerts(items) {
  const host = $('alertList');
  host.innerHTML = '';

  if (!items?.length) {
    host.innerHTML = '<div class="list-item"><span>No alerts logged yet.</span></div>';
    return;
  }

  items.forEach((item) => {
    const div = document.createElement('div');
    div.className = 'list-item';
    div.innerHTML = `
      <strong>${item.alert_type.replace('_', ' ')}</strong>
      <span>${item.day} • ${item.sent ? 'sent' : 'logged only'}</span>
    `;
    host.appendChild(div);
  });
}

async function refreshDashboard() {
  try {
    const response = await fetch('/api/status', { cache: 'no-store' });
    const data = await response.json();
    setTheme(data.flags);
    renderWeather(data.latest_weather);
    renderPrediction(data.prediction);
    renderSummaryList(data.daily_summaries);
    renderAlerts(data.alerts);
  } catch (error) {
    $('statusText').textContent = 'Unable to load dashboard data.';
  }
}

document.addEventListener("DOMContentLoaded", () => {
  refreshDashboard();
  setInterval(refreshDashboard, window.APP_CONFIG.refreshMs || 10800000);
});