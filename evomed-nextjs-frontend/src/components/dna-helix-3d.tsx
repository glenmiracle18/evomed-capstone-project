"use client";

import { Canvas, useFrame } from "@react-three/fiber";
import { OrbitControls } from "@react-three/drei";
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

// Enhanced base pair colors with more vibrant tone
const BASE_COLORS = {
  A: "#00ff88", // Adenine - Bright Green
  T: "#ff3366", // Thymine - Bright Red
  G: "#3366ff", // Guanine - Bright Blue
  C: "#ffdd00", // Cytosine - Bright Yellow
};

const COMPLEMENT: Record<string, string> = {
  A: "T",
  T: "A",
  G: "C",
  C: "G",
};

// Simplified base pair for reliable rendering
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
  const groupRef = useRef<THREE.Group>(null);

  // Animate mutation
  useFrame(({ clock }) => {
    if (isMutation && groupRef.current) {
      groupRef.current.rotation.z = Math.sin(clock.getElapsedTime() * 2) * 0.1;
    }
  });

  const color1 = BASE_COLORS[base1 as keyof typeof BASE_COLORS] || "#888888";
  const color2 = BASE_COLORS[base2 as keyof typeof BASE_COLORS] || "#888888";

  return (
    <group
      ref={groupRef}
      position={[0, yPosition, 0]}
      rotation={[0, rotation, 0]}
    >
      {/* Backbone spheres */}
      <mesh position={[2, 0, 0]}>
        <sphereGeometry args={[0.15, 16, 16]} />
        <meshStandardMaterial color={isMutation ? "#ff3366" : "#3c4f3d"} />
      </mesh>

      <mesh position={[-2, 0, 0]}>
        <sphereGeometry args={[0.15, 16, 16]} />
        <meshStandardMaterial color={isMutation ? "#ff3366" : "#3c4f3d"} />
      </mesh>

      {/* Base pairs */}
      <mesh
        position={[1.3, 0, 0]}
        onClick={onClick}
        onPointerOver={() => setHovered(true)}
        onPointerOut={() => setHovered(false)}
      >
        <boxGeometry args={[0.6, 0.2, 0.2]} />
        <meshStandardMaterial
          color={color1}
          emissive={isMutation || hovered ? color1 : "#000000"}
          emissiveIntensity={isMutation ? 0.5 : hovered ? 0.2 : 0}
        />
      </mesh>

      <mesh
        position={[-1.3, 0, 0]}
        onClick={onClick}
        onPointerOver={() => setHovered(true)}
        onPointerOut={() => setHovered(false)}
      >
        <boxGeometry args={[0.6, 0.2, 0.2]} />
        <meshStandardMaterial
          color={color2}
          emissive={isMutation || hovered ? color2 : "#000000"}
          emissiveIntensity={isMutation ? 0.5 : hovered ? 0.2 : 0}
        />
      </mesh>

      {/* Hydrogen bonds */}
      {isMutation ? (
        <>
          {/* Broken bonds */}
          <mesh position={[0.5, 0, 0]} rotation={[0, 0, Math.PI / 6]}>
            <cylinderGeometry args={[0.05, 0.05, 1.3, 8]} />
            <meshStandardMaterial
              color="#ff0000"
              emissive="#ff0000"
              emissiveIntensity={0.5}
            />
          </mesh>
          <mesh position={[-0.5, 0, 0]} rotation={[0, 0, -Math.PI / 6]}>
            <cylinderGeometry args={[0.05, 0.05, 1.3, 8]} />
            <meshStandardMaterial
              color="#ff0000"
              emissive="#ff0000"
              emissiveIntensity={0.5}
            />
          </mesh>
          {/* Mutation glow */}
          <mesh position={[0, 0, 0]}>
            <sphereGeometry args={[0.3, 16, 16]} />
            <meshStandardMaterial
              color="#ff3366"
              emissive="#ff0000"
              emissiveIntensity={1.0}
              transparent
              opacity={0.4}
            />
          </mesh>
        </>
      ) : (
        <mesh position={[0, 0, 0]} rotation={[0, 0, Math.PI / 2]}>
          <cylinderGeometry args={[0.05, 0.05, 2.6, 8]} />
          <meshStandardMaterial color="#cccccc" />
        </mesh>
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
  const helixRef = useRef<THREE.Group>(null);

  // Subtle rotation animation
  useFrame(() => {
    if (helixRef.current) {
      helixRef.current.rotation.y += 0.001;
    }
  });

  // Display first 60 bases for better performance
  const displaySequence = sequence.slice(0, 60).toUpperCase();

  const basePairs = useMemo(() => {
    const verticalSpacing = 0.35;
    const totalHeight = displaySequence.length * verticalSpacing;
    const centerOffset = -totalHeight / 2; // Center the helix vertically

    return displaySequence.split("").map((base, index) => {
      const position = startPosition + index;
      const complement = COMPLEMENT[base] || "N";
      const rotation = (index * Math.PI) / 5; // Twist angle for double helix
      const yPosition = index * verticalSpacing + centerOffset; // Center around origin
      const isMutation =
        mutationPosition !== null && position === mutationPosition;

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
    <group ref={helixRef}>
      {basePairs.map((bp, index) => (
        <BasePair
          key={index}
          {...bp}
          onClick={() => onBaseClick(bp.position, bp.base1)}
        />
      ))}
    </group>
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
      <div className="flex h-[500px] items-center justify-center rounded-lg border border-[#3c4f3d]/10 bg-white dark:border-[#3c4f3d]/20 dark:bg-[#242924]">
        <p className="text-sm text-[#3c4f3d]/60 dark:text-white/60">
          Load a gene sequence to view 3D DNA structure
        </p>
      </div>
    );
  }

  return (
    <div className="rounded-lg border border-[#3c4f3d]/10 bg-white shadow-lg dark:border-[#3c4f3d]/20 dark:bg-[#242924]">
      {/* Header */}
      <div className="border-b border-[#3c4f3d]/10 p-4 dark:border-[#3c4f3d]/20">
        <h3 className="text-lg font-semibold text-[#3c4f3d] dark:text-white">
          3D DNA Structure {geneName && `- ${geneName}`}
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
      <div className="relative h-[500px] bg-white dark:bg-[#242924]">
        <Canvas camera={{ position: [6, 0, 6], fov: 60 }}>
          <OrbitControls
            enableZoom={true}
            enablePan={true}
            enableRotate={true}
            autoRotate={true}
            autoRotateSpeed={1.0}
          />

          {/* Lighting */}
          <ambientLight intensity={1.0} />
          <directionalLight position={[5, 5, 5]} intensity={0.8} />

          {/* DNA Helix */}
          <Helix
            sequence={sequence}
            mutationPosition={mutationPosition}
            startPosition={startPosition}
            onBaseClick={handleBaseClick}
          />
        </Canvas>

        {/* Info Panel - pointer-events-none to allow interaction with canvas */}
        {selectedBase && (
          <div className="pointer-events-none absolute bottom-4 left-4 rounded-lg border border-[#3c4f3d]/20 bg-white/95 p-3 shadow-xl backdrop-blur-sm dark:border-[#3c4f3d]/40 dark:bg-[#242924]/95">
            <div className="text-xs font-semibold text-[#3c4f3d]/60 dark:text-white/60">
              Position: {selectedBase.position}
            </div>
            <div className="mt-1 flex items-center gap-2">
              <div
                className="h-3 w-3 rounded"
                style={{
                  backgroundColor:
                    BASE_COLORS[selectedBase.base as keyof typeof BASE_COLORS],
                }}
              />
              <span className="font-mono text-sm font-semibold text-[#3c4f3d] dark:text-white">
                {selectedBase.base} - {COMPLEMENT[selectedBase.base]}
              </span>
            </div>
          </div>
        )}
      </div>

      {/* Legend */}
      <div className="border-t border-[#3c4f3d]/10 p-4 dark:border-[#3c4f3d]/20">
        <div className="flex flex-wrap items-center gap-4 text-xs">
          <div className="flex items-center gap-2">
            <div className="h-3 w-3 rounded-sm bg-[#00ff88]" />
            <span className="text-[#3c4f3d]/70 dark:text-white/70">A</span>
          </div>
          <div className="flex items-center gap-2">
            <div className="h-3 w-3 rounded-sm bg-[#ff3366]" />
            <span className="text-[#3c4f3d]/70 dark:text-white/70">T</span>
          </div>
          <div className="flex items-center gap-2">
            <div className="h-3 w-3 rounded-sm bg-[#3366ff]" />
            <span className="text-[#3c4f3d]/70 dark:text-white/70">G</span>
          </div>
          <div className="flex items-center gap-2">
            <div className="h-3 w-3 rounded-sm bg-[#ffdd00]" />
            <span className="text-[#3c4f3d]/70 dark:text-white/70">C</span>
          </div>
        </div>
      </div>
    </div>
  );
}
