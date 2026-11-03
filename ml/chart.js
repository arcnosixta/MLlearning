/* All plot coordinates come from the corresponding Python laboratory. */
const mlPlotColors = ['#305db4', '#a14408', '#087b6c', '#8424a1', '#ab245c', '#51622c', '#145e78', '#756321', '#603853', '#3e465c'];

function mlExtent(values) {
  const lo = Math.min(...values), hi = Math.max(...values);
  const padding = lo === hi ? Math.max(1, Math.abs(lo) * .1) : (hi - lo) * .08;
  return [lo - padding, hi + padding];
}

function mlPlot(cases, current, topic, independentAxes, width) {
  const scaleCases = independentAxes ? [current] : cases;
  const all = scaleCases.flatMap(item => item.series.flatMap(series => series.points));
  const labels = [...new Set(cases.flatMap(item => item.series.map(series => mlText(series.label))))];
  const seriesColor = series => mlPlotColors[labels.indexOf(mlText(series.label)) % mlPlotColors.length];
  const bars = current.series.filter(series => series.kind === 'bar');
  const compact = width < 420;
  const [left, right, top, bottom] = [60, width - 27, 20, compact ? 181 : 238];
  const tickCount = compact ? 3 : 5;
  const xs = all.map(([x]) => x), ys = all.map(([, y]) => y);
  const [xmin, xmax] = mlExtent(xs);
  const [ymin, ymax] = mlExtent(scaleCases.some(item => item.series.some(series => series.kind === 'bar')) ? [...ys, 0] : ys);
  const sx = x => left + (x - xmin) * (right - left) / (xmax - xmin);
  const sy = y => bottom - (y - ymin) * (bottom - top) / (ymax - ymin);
  const fmt = new Intl.NumberFormat(window.ML_LOCALE, {maximumSignificantDigits: 4}).format;
  const yTicks = Array.from({length: tickCount}, (_, i) => ymin + (ymax - ymin) * i / (tickCount - 1));
  const xTicks = current.xTicks?.map(tick => [tick.value, mlText(tick.label)]) ??
    Array.from({length: tickCount}, (_, i) => xmin + (xmax - xmin) * i / (tickCount - 1)).map(x => [x, fmt(x)]);
  const barX = [...new Set(bars.flatMap(series => series.points.map(([x]) => sx(x))))].sort((a, b) => a - b);
  const gap = Math.min(54, ...barX.slice(1).map((x, i) => x - barX[i]));
  const barWidth = Math.max(1, gap * .78 / Math.max(1, bars.length));
  const marks = [...current.series.filter(series => !series.dashed), ...current.series.filter(series => series.dashed)].map(series => {
    const color = seriesColor(series);
    if (series.kind === 'line') {
      const points = series.points.map(([x, y]) => `${sx(x)},${sy(y)}`).join(' ');
      return `<polyline points="${points}" stroke="${color}" stroke-width="${series.dashed ? '2' : '3'}" ${series.dashed ? 'stroke-dasharray="5 4"' : ''} fill="none" stroke-linejoin="round"/>`;
    }
    if (series.kind === 'bar') {
      const offset = (bars.indexOf(series) - bars.length / 2) * barWidth;
      return series.points.map(([x, y]) => `<rect x="${sx(x) + offset}" y="${Math.min(sy(y), sy(0))}" width="${barWidth * .9}" height="${Math.max(1, Math.abs(sy(y) - sy(0)))}" fill="${color}"/>`).join('');
    }
    return series.points.map(([x, y]) => `<circle cx="${sx(x)}" cy="${sy(y)}" r="3.2" fill="${color}" opacity=".78"/>`).join('');
  }).join('');
  const textFit = (label, limit) => label.length * 6.5 > limit ? `textLength="${limit}" lengthAdjust="spacingAndGlyphs"` : '';
  const tickText = xTicks.map(([x, label]) => {
    const y = bottom + 17;
    const tilt = compact && current.xTicks && label.length > 5;
    const fit = tilt ? textFit(label, Math.min(74, (sx(x) - 6) / .81)) : '';
    return `<text x="${sx(x)}" y="${y}" text-anchor="${tilt ? 'end' : 'middle'}" ${tilt ? `transform="rotate(-36 ${sx(x)} ${y})"` : ''} ${fit}>${escapeHTML(label)}</text>`;
  }).join('');
  const xTitle = bottom + (compact && current.xTicks ? 61 : 43);
  return `<svg class="ml-plot" role="img" aria-label="${escapeHTML(`${topic.title} · ${mlText(current.label)} · ${topic.xLabel} / ${topic.yLabel}`)}" viewBox="0 0 ${width} ${xTitle + 9}">
    ${yTicks.map(y => `<path class="ml-gridline" d="M${left} ${sy(y)}H${right}"/><text x="${left - 8}" y="${sy(y) + 4}" text-anchor="end">${escapeHTML(fmt(y))}</text>`).join('')}
    <path class="ml-axis" d="M${left} ${top}V${bottom}H${right}"/>${marks}
    ${tickText}
    <text x="${(left + right) / 2}" y="${xTitle}" text-anchor="middle" ${textFit(topic.xLabel, right - left + 15)}>${escapeHTML(topic.xLabel)}</text>
    <text transform="translate(13 ${(top + bottom) / 2}) rotate(-90)" text-anchor="middle" ${textFit(topic.yLabel, bottom - top)}>${escapeHTML(topic.yLabel)}</text>
  </svg><ul class="ml-legend" aria-label="${jt('Легенда графика', 'График түсіндірмесі')}">${current.series.map(series => `<li><span ${series.dashed ? 'class="ml-dashed"' : ''} style="--series:${seriesColor(series)}"></span>${escapeHTML(mlText(series.label))}</li>`).join('')}</ul>`;
}

function mlChartTable(current, topic) {
  const rows = current.series.flatMap(series => series.points.map(([x, y]) => [
    mlText(series.label), mlText(current.xTicks?.find(tick => tick.value === x)?.label) ?? x, y
  ]));
  return `<table><thead><tr><th>${jt('Ряд', 'Қатар')}</th><th>${escapeHTML(topic.xLabel)}</th><th>${escapeHTML(topic.yLabel)}</th></tr></thead><tbody>${rows.map(row => `<tr>${row.map(cell => `<td>${escapeHTML(cell)}</td>`).join('')}</tr>`).join('')}</tbody></table>`;
}
