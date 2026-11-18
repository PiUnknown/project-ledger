"use client";

import {
  Bar,
  BarChart,
  CartesianGrid,
  Line,
  LineChart,
  ResponsiveContainer,
  Tooltip,
  XAxis,
  YAxis,
} from "recharts";
import { formatCell } from "@/lib/presentation";
import type { ChartPresentation as ChartPresentationData } from "@/lib/types";

const seriesColors = ["#4f7a5e", "#7c9c6f", "#2f5b44", "#a8b98f", "#6d8f8a"];

/**
 * Chart presentation. The chart is drawn from response rows only. A visually
 * hidden table repeats the same rows so the data stays accessible and the
 * renderer can be tested without relying on SVG geometry.
 */
export function ChartPresentation({
  presentation,
}: {
  presentation: ChartPresentationData;
}) {
  return (
    <figure className="chart-figure" data-chart-kind={presentation.kind}>
      <figcaption className="chart-title">{presentation.title}</figcaption>
      <div className="chart-canvas">
        <ResponsiveContainer width="100%" height={220}>
          {presentation.kind === "bar" ? (
            <BarChart
              data={presentation.rows}
              margin={{ top: 8, right: 16, bottom: 0, left: 0 }}
            >
              <CartesianGrid strokeDasharray="3 3" stroke="#e4e7e4" />
              <XAxis dataKey={presentation.x.key} tickLine={false} />
              <YAxis tickLine={false} width={40} />
              <Tooltip />
              {presentation.series.map((series, index) => (
                <Bar
                  key={series.key}
                  dataKey={series.key}
                  name={series.label}
                  fill={seriesColors[index % seriesColors.length]}
                  radius={[4, 4, 0, 0]}
                  maxBarSize={72}
                />
              ))}
            </BarChart>
          ) : (
            <LineChart
              data={presentation.rows}
              margin={{ top: 8, right: 16, bottom: 0, left: 0 }}
            >
              <CartesianGrid strokeDasharray="3 3" stroke="#e4e7e4" />
              <XAxis dataKey={presentation.x.key} tickLine={false} />
              <YAxis tickLine={false} width={40} />
              <Tooltip />
              {presentation.series.map((series, index) => (
                <Line
                  key={series.key}
                  type="monotone"
                  dataKey={series.key}
                  name={series.label}
                  stroke={seriesColors[index % seriesColors.length]}
                  strokeWidth={2}
                  dot={false}
                />
              ))}
            </LineChart>
          )}
        </ResponsiveContainer>
      </div>
      {presentation.truncated ? (
        <p className="chart-meta">Rows truncated to the configured row limit.</p>
      ) : null}
      <table className="sr-only">
        <caption>{presentation.title}</caption>
        <thead>
          <tr>
            <th scope="col">{presentation.x.label}</th>
            {presentation.series.map((series) => (
              <th key={series.key} scope="col">
                {series.label}
              </th>
            ))}
          </tr>
        </thead>
        <tbody>
          {presentation.rows.map((row, rowIndex) => (
            <tr key={rowIndex}>
              <td>{formatCell(row[presentation.x.key])}</td>
              {presentation.series.map((series) => (
                <td key={series.key}>{formatCell(row[series.key])}</td>
              ))}
            </tr>
          ))}
        </tbody>
      </table>
    </figure>
  );
}
