"use client";

import { Canvas } from "@react-three/fiber";
import { OrbitControls, Text, PerspectiveCamera } from "@react-three/drei";
import { useRef, useMemo, useState } from "react";
import * as THREE from "three";

interface DNAHelix3DProps {
  sequence: string;
  mutationPosition?: number | null;
  referenceBase?: string;
  alternateBase?: string;
  geneName?: string;
  startPosition?: number;
}

// Base pair colors (scientifically accurate)
const BASE_COLORS = {
  A: "#00ff00", // Adenine - Green
  T: "#ff0000", // Thymine - Red
  G: "#0000ff", // Guanine - Blue
  C: "#ffff00", // Cytosine - Yellow
};

// Complementary base pairs
const COMPLEMENT: Record<string, string> = {
  A: "T",
  T: "A",
  G: "C",
  C: "G",
};

function BasePair({
  base1,
  base2,
  position,
  yPosition,
  rotation,
  isMutation,
  onClick,
}: {
  base1: string;
  base2: string;
  position: number;
  yPosition: number;
  rotation: number;
  isMutation: boolean;
  onClick: () => void;
}) {
  const [hovered, setHovered] = useState(false);

  const color1 = BASE_COLORS[base1 as keyof typeof BASE_COLORS] || "#888888";
  const color2 = BASE_COLORS[base2 as keyof typeof BASE_COLORS] || "#888888";

  return (
    <group position={[0, yPosition, 0]} rotation={[0, rotation, 0]}>
      {/* Strand 1 backbone sphere */}
      <mesh position={[2, 0, 0]}>
        <sphereGeometry args={[0.15, 16, 16]} />
        <meshStandardMaterial
          color={isMutation ? "#de8246" : "#3c4f3d"}
          emissive={isMutation ? "#de8246" : "#000000"}
          emissiveIntensity={isMutation ? 0.5 : 0}
        />
      </mesh>

      {/* Strand 2 backbone sphere */}
      <mesh position={[-2, 0, 0]}>
        <sphereGeometry args={[0.15, 16, 16]} />
        <meshStandardMaterial
          color={isMutation ? "#de8246" : "#3c4f3d"}
          emissive={isMutation ? "#de8246" : "#000000"}
          emissiveIntensity={isMutation ? 0.5 : 0}
        />
      </mesh>

      {/* Base 1 (right side) */}
      <mesh
        position={[1.3, 0, 0]}
        onClick={onClick}
        onPointerOver={() => setHovered(true)}
        onPointerOut={() => setHovered(false)}
      >
        <boxGeometry args={[0.6, 0.2, 0.2]} />
        <meshStandardMaterial
          color={color1}
          emissive={isMutation ? "#ff0000" : hovered ? "#ffffff" : "#000000"}
          emissiveIntensity={isMutation ? 0.8 : hovered ? 0.3 : 0}
        />
      </mesh>

      {/* Base 2 (left side) */}
      <mesh
        position={[-1.3, 0, 0]}
        onClick={onClick}
        onPointerOver={() => setHovered(true)}
        onPointerOut={() => setHovered(false)}
      >
        <boxGeometry args={[0.6, 0.2, 0.2]} />
        <meshStandardMaterial
          color={color2}
          emissive={isMutation ? "#ff0000" : hovered ? "#ffffff" : "#000000"}
          emissiveIntensity={isMutation ? 0.8 : hovered ? 0.3 : 0}
        />
      </mesh>

      {/* Connecting hydrogen bonds */}
      <mesh position={[0, 0, 0]}>
        <cylinderGeometry args={[0.05, 0.05, 2.6, 8]} />
        <meshStandardMaterial
          color={isMutation ? "#ff6b6b" : "#cccccc"}
          opacity={0.6}
          transparent
        />
      </mesh>

      {/* Position label (only show every 10th) */}
      {position % 10 === 0 && (
        <Text
          position={[3, 0, 0]}
          fontSize={0.15}
          color={isMutation ? "#de8246" : "#3c4f3d"}
          anchorX="left"
        >
          {position}
        </Text>
      )}
    </group>
  );
}

function Helix({
  sequence,
  mutationPosition,
  startPosition = 1,
  onBaseClick,
}: {
  sequence: string;
  mutationPosition?: number | null;
  startPosition?: number;
  onBaseClick: (position: number, base: string) => void;
}) {
  // Limit to first 100 bases for performance
  const displaySequence = sequence.slice(0, 100).toUpperCase();

  const basePairs = useMemo(() => {
    return displaySequence.split("").map((base, index) => {
      const position = startPosition + index;
      const complement = COMPLEMENT[base] || "N";
      const rotation = (index * Math.PI) / 5; // Twist angle
      const yPosition = index * 0.3; // Vertical spacing
      const isMutation = mutationPosition !== null && position === mutationPosition;

      return {
        base1: base,
        base2: complement,
        position,
        yPosition,
        rotation,
        isMutation,
      };
    });
  }, [displaySequence, mutationPosition, startPosition]);

  return (
    <>
      {basePairs.map((bp, index) => (
        <BasePair
          key={index}
          {...bp}
          onClick={() => onBaseClick(bp.position, bp.base1)}
        />
      ))}
    </>
  );
}

export function DNAHelix3D({
  sequence,
  mutationPosition,
  referenceBase,
  alternateBase,
  geneName,
  startPosition,
}: DNAHelix3DProps) {
  const [selectedBase, setSelectedBase] = useState<{
    position: number;
    base: string;
  } | null>(null);

  const handleBaseClick = (position: number, base: string) => {
    setSelectedBase({ position, base });
  };

  if (!sequence || sequence.length === 0) {
    return (
      <div className="flex h-96 items-center justify-center rounded-lg border border-[#3c4f3d]/10 bg-white dark:border-[#3c4f3d]/20 dark:bg-[#242924]">
        <p className="text-sm text-[#3c4f3d]/60 dark:text-white/60">
          No sequence data available for 3D visualization
        </p>
      </div>
    );
  }

  return (
    <div className="rounded-lg border border-[#3c4f3d]/10 bg-white dark:border-[#3c4f3d]/20 dark:bg-[#242924]">
      {/* Header */}
      <div className="border-b border-[#3c4f3d]/10 p-4 dark:border-[#3c4f3d]/20">
        <h3 className="text-lg font-semibold text-[#3c4f3d] dark:text-white">
          3D DNA Helix Visualization {geneName && `- ${geneName}`}
        </h3>
        {mutationPosition && (
          <p className="mt-1 text-sm text-[#3c4f3d]/70 dark:text-white/70">
            Mutation at position {mutationPosition}:{" "}
            <span className="font-mono font-semibold text-[#de8246]">
              {referenceBase} → {alternateBase}
            </span>
          </p>
        )}
      </div>

      {/* 3D Canvas */}
      <div className="relative h-96">
        <Canvas>
          <PerspectiveCamera makeDefault position={[8, 15, 8]} />
          <OrbitControls
            enableZoom={true}
            enablePan={true}
            enableRotate={true}
            autoRotate={true}
            autoRotateSpeed={0.5}
          />

          {/* Lighting */}
          <ambientLight intensity={0.5} />
          <directionalLight position={[10, 10, 5]} intensity={1} />
          <pointLight position={[-10, -10, -5]} intensity={0.5} />

          {/* DNA Helix */}
          <Helix
            sequence={sequence}
            mutationPosition={mutationPosition}
            startPosition={startPosition}
            onBaseClick={handleBaseClick}
          />
        </Canvas>

        {/* Info Panel */}
        {selectedBase && (
          <div className="absolute bottom-4 left-4 rounded-lg border border-[#3c4f3d]/20 bg-white/95 p-3 shadow-lg dark:bg-[#242924]/95">
            <div className="text-xs text-[#3c4f3d]/60 dark:text-white/60">
              Selected Base
            </div>
            <div className="mt-1 font-mono text-sm font-semibold text-[#3c4f3d] dark:text-white">
              Position: {selectedBase.position}
            </div>
            <div className="font-mono text-sm font-semibold text-[#3c4f3d] dark:text-white">
              Base: {selectedBase.base} (pairs with {COMPLEMENT[selectedBase.base]})
            </div>
          </div>
        )}
      </div>

      {/* Legend */}
      <div className="border-t border-[#3c4f3d]/10 p-4 dark:border-[#3c4f3d]/20">
        <div className="flex items-center gap-6 text-xs">
          <div className="flex items-center gap-2">
            <div className="h-3 w-3 rounded-sm bg-[#00ff00]" />
            <span className="text-[#3c4f3d]/70 dark:text-white/70">A (Adenine)</span>
          </div>
          <div className="flex items-center gap-2">
            <div className="h-3 w-3 rounded-sm bg-[#ff0000]" />
            <span className="text-[#3c4f3d]/70 dark:text-white/70">T (Thymine)</span>
          </div>
          <div className="flex items-center gap-2">
            <div className="h-3 w-3 rounded-sm bg-[#0000ff]" />
            <span className="text-[#3c4f3d]/70 dark:text-white/70">G (Guanine)</span>
          </div>
          <div className="flex items-center gap-2">
            <div className="h-3 w-3 rounded-sm bg-[#ffff00]" />
            <span className="text-[#3c4f3d]/70 dark:text-white/70">C (Cytosine)</span>
          </div>
          {mutationPosition && (
            <div className="ml-auto flex items-center gap-2">
              <div className="h-3 w-3 rounded-sm bg-[#de8246]" />
              <span className="text-[#3c4f3d]/70 dark:text-white/70">Mutation</span>
            </div>
          )}
        </div>
        <div className="mt-2 text-xs text-[#3c4f3d]/50 dark:text-white/50">
          Drag to rotate • Scroll to zoom • Click base pairs for details
        </div>
      </div>
    </div>
  );
}
