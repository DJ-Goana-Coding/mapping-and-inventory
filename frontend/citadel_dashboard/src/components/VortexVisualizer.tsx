/**
 * ═══════════════════════════════════════════════════════════════════════════
 * VORTEX VISUALISER — 3D PeaceVortex Data Flow (v22.2121)
 * ═══════════════════════════════════════════════════════════════════════════
 * 3D rendering of the PeaceVortex data flow using Three.js / R3F.
 * Displays real-time data streams as a toroidal vortex.
 * Part of the Citadel Cockpit — Q.G.T.N.L. Command Citadel
 * ═══════════════════════════════════════════════════════════════════════════
 */

import React, { useRef, useMemo } from "react";
import { Canvas, useFrame } from "@react-three/fiber";
import { OrbitControls, Text } from "@react-three/drei";
import * as THREE from "three";

/** Vortex configuration */
export const VORTEX_PARTICLE_COUNT = 2000;
export const VORTEX_RADIUS = 3;
export const VORTEX_TUBE_RADIUS = 1;

export interface VortexDataPoint {
  label: string;
  value: number;
  colour: string;
}

export interface VortexVisualizerProps {
  /** Data points to visualise in the vortex */
  dataPoints?: VortexDataPoint[];
  /** Rotation speed multiplier (default 1.0) */
  speed?: number;
  /** Canvas height in pixels */
  height?: number;
}

/**
 * Particle system orbiting a toroidal path — represents data
 * flowing through the PeaceVortex pipeline.
 */
const VortexParticles: React.FC<{ speed: number }> = ({ speed }) => {
  const meshRef = useRef<THREE.Points>(null);

  const positions = useMemo(() => {
    const arr = new Float32Array(VORTEX_PARTICLE_COUNT * 3);
    for (let i = 0; i < VORTEX_PARTICLE_COUNT; i++) {
      const theta = Math.random() * Math.PI * 2;
      const phi = Math.random() * Math.PI * 2;
      const r = VORTEX_RADIUS + VORTEX_TUBE_RADIUS * Math.cos(phi);

      arr[i * 3] = r * Math.cos(theta);
      arr[i * 3 + 1] = VORTEX_TUBE_RADIUS * Math.sin(phi);
      arr[i * 3 + 2] = r * Math.sin(theta);
    }
    return arr;
  }, []);

  const colours = useMemo(() => {
    const arr = new Float32Array(VORTEX_PARTICLE_COUNT * 3);
    const palette = [
      new THREE.Color("#2ECC71"),
      new THREE.Color("#4A90D9"),
      new THREE.Color("#E74C3C"),
      new THREE.Color("#F39C12"),
      new THREE.Color("#9B59B6"),
    ];
    for (let i = 0; i < VORTEX_PARTICLE_COUNT; i++) {
      const c = palette[i % palette.length];
      arr[i * 3] = c.r;
      arr[i * 3 + 1] = c.g;
      arr[i * 3 + 2] = c.b;
    }
    return arr;
  }, []);

  useFrame((_, delta) => {
    if (meshRef.current) {
      meshRef.current.rotation.y += delta * 0.3 * speed;
      meshRef.current.rotation.x += delta * 0.1 * speed;
    }
  });

  return (
    <points ref={meshRef}>
      <bufferGeometry>
        <bufferAttribute
          attach="attributes-position"
          args={[positions, 3]}
        />
        <bufferAttribute
          attach="attributes-color"
          args={[colours, 3]}
        />
      </bufferGeometry>
      <pointsMaterial
        size={0.04}
        vertexColors
        transparent
        opacity={0.8}
        sizeAttenuation
      />
    </points>
  );
};

/**
 * Toroidal wireframe — the structural skeleton of the vortex.
 */
const VortexSkeleton: React.FC<{ speed: number }> = ({ speed }) => {
  const meshRef = useRef<THREE.Mesh>(null);

  useFrame((_, delta) => {
    if (meshRef.current) {
      meshRef.current.rotation.y += delta * 0.15 * speed;
    }
  });

  return (
    <mesh ref={meshRef}>
      <torusGeometry args={[VORTEX_RADIUS, VORTEX_TUBE_RADIUS, 32, 64]} />
      <meshBasicMaterial
        color="#4A90D9"
        wireframe
        transparent
        opacity={0.15}
      />
    </mesh>
  );
};

/**
 * Floating data labels around the vortex.
 */
const DataLabels: React.FC<{ dataPoints: VortexDataPoint[] }> = ({
  dataPoints,
}) => {
  return (
    <>
      {dataPoints.map((dp, i) => {
        const angle = (i / dataPoints.length) * Math.PI * 2;
        const r = VORTEX_RADIUS + VORTEX_TUBE_RADIUS + 1;
        const x = r * Math.cos(angle);
        const z = r * Math.sin(angle);

        return (
          <Text
            key={dp.label}
            position={[x, 0.5, z]}
            fontSize={0.25}
            color={dp.colour}
            anchorX="center"
            anchorY="middle"
          >
            {`${dp.label}: ${dp.value}`}
          </Text>
        );
      })}
    </>
  );
};

/**
 * VortexVisualizer — 3D PeaceVortex data flow renderer.
 *
 * Uses React Three Fiber to render particles flowing along a
 * toroidal path, representing the interconnected data streams
 * of the Citadel Mesh.
 */
export const VortexVisualizer: React.FC<VortexVisualizerProps> = ({
  dataPoints,
  speed = 1.0,
  height = 400,
}) => {
  const defaultData: VortexDataPoint[] = [
    { label: "Sniper", value: 56, colour: "#E74C3C" },
    { label: "Trend", value: 78, colour: "#2ECC71" },
    { label: "Volatility", value: 42, colour: "#F39C12" },
    { label: "Commander", value: 93, colour: "#4A90D9" },
    { label: "PvC Ledger", value: 100, colour: "#9B59B6" },
    { label: "Mirror", value: 88, colour: "#1ABC9C" },
  ];

  const points = dataPoints ?? defaultData;

  return (
    <div
      style={{
        width: "100%",
        height: `${height}px`,
        borderRadius: "12px",
        overflow: "hidden",
        backgroundColor: "#0D0D1A",
        border: "1px solid #4A90D940",
      }}
    >
      <Canvas
        camera={{ position: [0, 4, 8], fov: 50 }}
        style={{ background: "transparent" }}
      >
        <ambientLight intensity={0.3} />
        <pointLight position={[10, 10, 10]} intensity={0.5} />

        <VortexParticles speed={speed} />
        <VortexSkeleton speed={speed} />
        <DataLabels dataPoints={points} />

        <OrbitControls
          enableZoom={true}
          enablePan={false}
          autoRotate
          autoRotateSpeed={0.5 * speed}
        />
      </Canvas>

      {/* Overlay label */}
      <div
        style={{
          position: "relative",
          bottom: "40px",
          textAlign: "center",
          color: "#4A90D9",
          fontSize: "12px",
          fontFamily: "'Segoe UI', system-ui, sans-serif",
          pointerEvents: "none",
        }}
      >
        🌀 PeaceVortex Data Flow — {points.length} Streams Active
      </div>
    </div>
  );
};

export default VortexVisualizer;
