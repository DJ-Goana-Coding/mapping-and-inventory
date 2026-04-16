/**
 * ═══════════════════════════════════════════════════════════════════════════
 * STABILITY METER — Real-Time System Stability Visualiser (v22.2121)
 * ═══════════════════════════════════════════════════════════════════════════
 * Displays the 9,293 Stability constant and 144Hz Sync frequency
 * as a real-time visual gauge.
 * Part of the Citadel Cockpit — Q.G.T.N.L. Command Citadel
 * ═══════════════════════════════════════════════════════════════════════════
 */

import React, { useEffect, useState, useRef } from "react";

/** Stability constants */
export const STABILITY_CONSTANT = 9293;
export const SYNC_FREQUENCY_HZ = 144;
export const MAX_STABILITY = 10000;

export interface StabilityData {
  /** Current stability value (0–10,000) */
  currentStability: number;
  /** Current sync frequency in Hz */
  syncFrequency: number;
  /** System uptime percentage */
  uptime: number;
  /** Number of active nodes */
  activeNodes: number;
  /** Total nodes */
  totalNodes: number;
}

export interface StabilityMeterProps {
  /** Current stability data — defaults to baseline if omitted */
  data?: Partial<StabilityData>;
  /** Auto-refresh interval in milliseconds (0 = disabled) */
  refreshInterval?: number;
}

/**
 * StabilityMeter — Real-time visualisation of the Citadel stability
 * constant and 144Hz synchronisation frequency.
 */
export const StabilityMeter: React.FC<StabilityMeterProps> = ({
  data,
  refreshInterval = 0,
}) => {
  const [stability, setStability] = useState<StabilityData>({
    currentStability: data?.currentStability ?? STABILITY_CONSTANT,
    syncFrequency: data?.syncFrequency ?? SYNC_FREQUENCY_HZ,
    uptime: data?.uptime ?? 99.97,
    activeNodes: data?.activeNodes ?? 8,
    totalNodes: data?.totalNodes ?? 8,
  });

  const canvasRef = useRef<HTMLCanvasElement>(null);
  const animFrameRef = useRef<number>(0);

  // Update stability when props change
  useEffect(() => {
    if (data) {
      setStability((prev) => ({ ...prev, ...data }));
    }
  }, [data]);

  // Simulate pulse animation (144Hz visual representation)
  useEffect(() => {
    const canvas = canvasRef.current;
    if (!canvas) return;
    const ctx = canvas.getContext("2d");
    if (!ctx) return;

    let phase = 0;

    const draw = () => {
      const w = canvas.width;
      const h = canvas.height;
      ctx.clearRect(0, 0, w, h);

      // Draw 144Hz sine wave
      ctx.beginPath();
      ctx.strokeStyle = "#2ECC71";
      ctx.lineWidth = 2;

      const frequency = stability.syncFrequency / 30; // Visual scaling
      const amplitude = h * 0.3;
      const midY = h / 2;

      for (let x = 0; x < w; x++) {
        const y =
          midY + amplitude * Math.sin((x / w) * Math.PI * 2 * frequency + phase);
        if (x === 0) ctx.moveTo(x, y);
        else ctx.lineTo(x, y);
      }
      ctx.stroke();

      // Stability indicator line
      const stabilityRatio = stability.currentStability / MAX_STABILITY;
      const indicatorY = h - h * stabilityRatio;
      ctx.beginPath();
      ctx.strokeStyle = stabilityRatio >= 0.9 ? "#2ECC71" : "#E67E22";
      ctx.setLineDash([5, 5]);
      ctx.moveTo(0, indicatorY);
      ctx.lineTo(w, indicatorY);
      ctx.stroke();
      ctx.setLineDash([]);

      phase += 0.05;
      animFrameRef.current = requestAnimationFrame(draw);
    };

    draw();

    return () => {
      cancelAnimationFrame(animFrameRef.current);
    };
  }, [stability]);

  const stabilityPct =
    (stability.currentStability / MAX_STABILITY) * 100;
  const isHealthy = stabilityPct >= 90;

  return (
    <div
      style={{
        padding: "16px",
        fontFamily: "'Segoe UI', system-ui, sans-serif",
        color: "#E0E0E0",
        backgroundColor: "#1A1A2E",
        borderRadius: "12px",
        border: `1px solid ${isHealthy ? "#2ECC71" : "#E67E22"}40`,
      }}
    >
      <h3 style={{ margin: "0 0 16px", fontSize: "16px" }}>
        📊 Stability Meter
      </h3>

      {/* Main gauge */}
      <div style={{ display: "flex", alignItems: "center", gap: "24px" }}>
        {/* Numerical display */}
        <div style={{ textAlign: "center" }}>
          <div
            style={{
              fontSize: "48px",
              fontWeight: 700,
              color: isHealthy ? "#2ECC71" : "#E67E22",
              fontVariantNumeric: "tabular-nums",
            }}
          >
            {stability.currentStability.toLocaleString()}
          </div>
          <div style={{ fontSize: "12px", color: "#888" }}>
            / {MAX_STABILITY.toLocaleString()} Stability
          </div>
        </div>

        {/* Waveform canvas */}
        <canvas
          ref={canvasRef}
          width={300}
          height={80}
          style={{
            flex: 1,
            borderRadius: "8px",
            backgroundColor: "#0D0D1A",
          }}
        />
      </div>

      {/* Stats row */}
      <div
        style={{
          display: "flex",
          gap: "16px",
          marginTop: "16px",
          justifyContent: "space-between",
        }}
      >
        <StatCard
          label="Sync Frequency"
          value={`${stability.syncFrequency} Hz`}
          colour="#4A90D9"
        />
        <StatCard
          label="Uptime"
          value={`${stability.uptime.toFixed(2)}%`}
          colour="#2ECC71"
        />
        <StatCard
          label="Active Nodes"
          value={`${stability.activeNodes}/${stability.totalNodes}`}
          colour="#E74C3C"
        />
        <StatCard
          label="Health"
          value={isHealthy ? "NOMINAL" : "DEGRADED"}
          colour={isHealthy ? "#2ECC71" : "#E67E22"}
        />
      </div>

      {/* Progress bar */}
      <div
        style={{
          marginTop: "12px",
          height: "6px",
          borderRadius: "3px",
          backgroundColor: "#333",
          overflow: "hidden",
        }}
      >
        <div
          style={{
            width: `${stabilityPct}%`,
            height: "100%",
            borderRadius: "3px",
            backgroundColor: isHealthy ? "#2ECC71" : "#E67E22",
            transition: "width 0.5s ease",
          }}
        />
      </div>
    </div>
  );
};

/** Small stat card sub-component */
const StatCard: React.FC<{
  label: string;
  value: string;
  colour: string;
}> = ({ label, value, colour }) => (
  <div
    style={{
      textAlign: "center",
      padding: "8px 16px",
      borderRadius: "8px",
      backgroundColor: `${colour}10`,
      border: `1px solid ${colour}30`,
    }}
  >
    <div style={{ fontSize: "18px", fontWeight: 700, color: colour }}>
      {value}
    </div>
    <div style={{ fontSize: "11px", color: "#888" }}>{label}</div>
  </div>
);

export default StabilityMeter;
