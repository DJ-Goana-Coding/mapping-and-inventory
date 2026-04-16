/**
 * ═══════════════════════════════════════════════════════════════════════════
 * PERSONA SWITCHER — Multi-Persona Toggle Component (v22.2121)
 * ═══════════════════════════════════════════════════════════════════════════
 * Seamlessly toggle between Systems Architect, Quant Trader, and DJ Goanna.
 * Part of the Citadel Cockpit — Q.G.T.N.L. Command Citadel
 * ═══════════════════════════════════════════════════════════════════════════
 */

import React, { useState, useCallback } from "react";

/** Available Citadel personas */
export interface Persona {
  id: string;
  name: string;
  icon: string;
  description: string;
  colour: string;
  modules: string[];
}

export const PERSONAS: Persona[] = [
  {
    id: "systems-architect",
    name: "Systems Architect",
    icon: "🏛️",
    description:
      "Full-stack infrastructure oversight — Citadel Mesh, Districts, Workflows",
    colour: "#4A90D9",
    modules: [
      "District Manager",
      "Workflow Engine",
      "ARK-CORE Sync",
      "Security Sentinel",
    ],
  },
  {
    id: "quant-trader",
    name: "Quant Trader",
    icon: "💹",
    description:
      "Harvest Moon Trader — XRP/Ripple Quant-Hub with PvC Ledger integration",
    colour: "#2ECC71",
    modules: [
      "Harvest Moon Trader",
      "PvC Ledger",
      "Market Sensor",
      "Profit Sentry",
    ],
  },
  {
    id: "dj-goanna",
    name: "DJ Goanna",
    icon: "🦎",
    description:
      "Creative intelligence — Music production, media, and artistic expression",
    colour: "#E74C3C",
    modules: [
      "Media Coding",
      "Audio Engine",
      "Visual Designer",
      "Creative RAG",
    ],
  },
];

export interface PersonaSwitcherProps {
  /** Currently active persona ID */
  activePersonaId?: string;
  /** Callback when persona is switched */
  onSwitch?: (persona: Persona) => void;
}

/**
 * PersonaSwitcher — Toggle between Citadel personas.
 *
 * Renders a horizontal selector with persona cards. Each card shows
 * the persona icon, name, description, and available modules.
 */
export const PersonaSwitcher: React.FC<PersonaSwitcherProps> = ({
  activePersonaId,
  onSwitch,
}) => {
  const [active, setActive] = useState<string>(
    activePersonaId ?? PERSONAS[0].id,
  );

  const handleSwitch = useCallback(
    (persona: Persona) => {
      setActive(persona.id);
      onSwitch?.(persona);
    },
    [onSwitch],
  );

  const activePersona = PERSONAS.find((p) => p.id === active) ?? PERSONAS[0];

  return (
    <div
      style={{
        display: "flex",
        flexDirection: "column",
        gap: "16px",
        padding: "16px",
        fontFamily: "'Segoe UI', system-ui, sans-serif",
      }}
    >
      {/* Persona selector */}
      <div
        style={{
          display: "flex",
          gap: "12px",
          justifyContent: "center",
        }}
      >
        {PERSONAS.map((persona) => (
          <button
            key={persona.id}
            onClick={() => handleSwitch(persona)}
            aria-pressed={persona.id === active}
            style={{
              display: "flex",
              alignItems: "center",
              gap: "8px",
              padding: "12px 24px",
              border: `2px solid ${persona.id === active ? persona.colour : "#333"}`,
              borderRadius: "8px",
              backgroundColor:
                persona.id === active ? persona.colour + "20" : "transparent",
              color: persona.id === active ? persona.colour : "#ccc",
              cursor: "pointer",
              fontSize: "16px",
              fontWeight: persona.id === active ? 700 : 400,
              transition: "all 0.2s ease",
            }}
          >
            <span style={{ fontSize: "24px" }}>{persona.icon}</span>
            <span>{persona.name}</span>
          </button>
        ))}
      </div>

      {/* Active persona detail */}
      <div
        style={{
          padding: "16px",
          border: `1px solid ${activePersona.colour}40`,
          borderRadius: "8px",
          backgroundColor: `${activePersona.colour}10`,
        }}
      >
        <div style={{ display: "flex", alignItems: "center", gap: "8px" }}>
          <span style={{ fontSize: "32px" }}>{activePersona.icon}</span>
          <div>
            <h3
              style={{
                margin: 0,
                color: activePersona.colour,
                fontSize: "18px",
              }}
            >
              {activePersona.name}
            </h3>
            <p style={{ margin: "4px 0 0", color: "#999", fontSize: "14px" }}>
              {activePersona.description}
            </p>
          </div>
        </div>

        {/* Module badges */}
        <div
          style={{
            display: "flex",
            gap: "8px",
            marginTop: "12px",
            flexWrap: "wrap",
          }}
        >
          {activePersona.modules.map((mod) => (
            <span
              key={mod}
              style={{
                padding: "4px 12px",
                borderRadius: "16px",
                backgroundColor: `${activePersona.colour}30`,
                color: activePersona.colour,
                fontSize: "12px",
                fontWeight: 600,
              }}
            >
              {mod}
            </span>
          ))}
        </div>
      </div>
    </div>
  );
};

export default PersonaSwitcher;
