"use client";

import { Canvas, useFrame } from "@react-three/fiber";
import { OrbitControls, Text, PerspectiveCamera, MeshDistortMaterial, Sphere } from "@react-three/drei";
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

// Enhanced base pair colors with more vibrant tones
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

// Animated mutation particle effect
function MutationParticles({ position }: { position: [number, number, number] }) {
  const particlesRef = useRef<THREE.Points>(null);

  useFrame(({ clock }) => {
    if (particlesRef.current) {
      particlesRef.current.rotation.y = clock.getElapsedTime() * 0.5;
    }
  });

  const particles = useMemo(() => {
    const positions = [];
    for (let i = 0; i < 50; i++) {
      const theta = Math.random() * Math.PI * 2;
      const radius = 0.3 + Math.random() * 0.5;
      positions.push(
        Math.cos(theta) * radius,
        (Math.random() - 0.5) * 0.5,
        Math.sin(theta) * radius
      );
    }
    return new Float32Array(positions);
  }, []);

  return (
    <points ref={particlesRef} position={position}>
      <bufferGeometry>
        <bufferAttribute
          attach="attributes-position"
          count={particles.length / 3}
          array={particles}
          itemSize={3}
        />
      </bufferGeometry>
      <pointsMaterial
        size={0.05}
        color="#ff0000"
        transparent
        opacity={0.8}
        sizeAttenuation
      />
    </points>
  );
}

// Enhanced base pair with better materials and mutation effects
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
  const mutationRef = useRef<THREE.Mesh>(null);

  // Animate mutation pulsing
  useFrame(({ clock }) => {
    if (isMutation && mutationRef.current) {
      const scale = 1 + Math.sin(clock.getElapsedTime() * 3) * 0.15;
      mutationRef.current.scale.set(scale, scale, scale);
    }
    if (isMutation && groupRef.current) {
      // Slight wobble for mutation
      groupRef.current.rotation.z = Math.sin(clock.getElapsedTime() * 2) * 0.1;
    }
  });

  const color1 = BASE_COLORS[base1 as keyof typeof BASE_COLORS] || "#888888";
  const color2 = BASE_COLORS[base2 as keyof typeof BASE_COLORS] || "#888888";

  // Mutation distorts the structure
  const distortion = isMutation ? 0.4 : 0;

  return (
    <group ref={groupRef} position={[0, yPosition, 0]} rotation={[0, rotation, 0]}>
      {/* Enhanced backbone spheres with metallic material */}
      <mesh position={[2.2, 0, 0]}>
        <sphereGeometry args={[0.18, 32, 32]} />
        <meshStandardMaterial
          color={isMutation ? "#ff3366" : "#2d3d2e"}
          emissive={isMutation ? "#ff0000" : "#000000"}
          emissiveIntensity={isMutation ? 1.2 : 0}
          metalness={0.7}
          roughness={0.3}
        />
      </mesh>

      <mesh position={[-2.2, 0, 0]}>
        <sphereGeometry args={[0.18, 32, 32]} />
        <meshStandardMaterial
          color={isMutation ? "#ff3366" : "#2d3d2e"}
          emissive={isMutation ? "#ff0000" : "#000000"}
          emissiveIntensity={isMutation ? 1.2 : 0}
          metalness={0.7}
          roughness={0.3}
        />
      </mesh>

      {/* Connecting backbone tubes for continuous strand appearance */}
      {position % 2 === 0 && (
        <>
          <mesh position={[2.2, 0.15, 0]} rotation={[0, rotation * 0.2, 0]}>
            <cylinderGeometry args={[0.08, 0.08, 0.3, 16]} />
            <meshStandardMaterial
              color={isMutation ? "#ff3366" : "#3c4f3d"}
              metalness={0.5}
              roughness={0.4}
            />
          </mesh>
          <mesh position={[-2.2, 0.15, 0]} rotation={[0, rotation * 0.2, 0]}>
            <cylinderGeometry args={[0.08, 0.08, 0.3, 16]} />
            <meshStandardMaterial
              color={isMutation ? "#ff3366" : "#3c4f3d"}
              metalness={0.5}
              roughness={0.4}
            />
          </mesh>
        </>
      )}

      {/* Enhanced base representations with better geometry */}
      <mesh
        position={[1.4, 0, 0]}
        onClick={onClick}
        onPointerOver={() => setHovered(true)}
        onPointerOut={() => setHovered(false)}
      >
        <boxGeometry args={[0.7, 0.25, 0.25]} />
        <meshStandardMaterial
          color={color1}
          emissive={isMutation ? "#ff6600" : hovered ? color1 : "#000000"}
          emissiveIntensity={isMutation ? 0.9 : hovered ? 0.4 : 0}
          metalness={0.6}
          roughness={0.2}
        />
      </mesh>

      <mesh
        position={[-1.4, 0, 0]}
        onClick={onClick}
        onPointerOver={() => setHovered(true)}
        onPointerOut={() => setHovered(false)}
      >
        <boxGeometry args={[0.7, 0.25, 0.25]} />
        <meshStandardMaterial
          color={color2}
          emissive={isMutation ? "#ff6600" : hovered ? color2 : "#000000"}
          emissiveIntensity={isMutation ? 0.9 : hovered ? 0.4 : 0}
          metalness={0.6}
          roughness={0.2}
        />
      </mesh>

      {/* Hydrogen bonds - break/distort for mutations */}
      {isMutation ? (
        <>
          {/* Broken bonds for mutation */}
          <mesh position={[0.5, 0, 0]} rotation={[0, 0, Math.PI / 6]}>
            <cylinderGeometry args={[0.06, 0.06, 1.5, 8]} />
            <meshStandardMaterial
              color="#ff0000"
              opacity={0.7}
              transparent
              emissive="#ff0000"
              emissiveIntensity={0.8}
            />
          </mesh>
          <mesh position={[-0.5, 0, 0]} rotation={[0, 0, -Math.PI / 6]}>
            <cylinderGeometry args={[0.06, 0.06, 1.5, 8]} />
            <meshStandardMaterial
              color="#ff0000"
              opacity={0.7}
              transparent
              emissive="#ff0000"
              emissiveIntensity={0.8}
            />
          </mesh>
          {/* Mutation marker - glowing sphere */}
          <mesh ref={mutationRef} position={[0, 0, 0]}>
            <sphereGeometry args={[0.35, 32, 32]} />
            <meshStandardMaterial
              color="#ff3366"
              emissive="#ff0000"
              emissiveIntensity={1.5}
              transparent
              opacity={0.6}
              metalness={0.8}
              roughness={0.1}
            />
          </mesh>
          {/* Mutation particles */}
          <MutationParticles position={[0, 0, 0]} />
        </>
      ) : (
        /* Normal hydrogen bonds */
        <mesh position={[0, 0, 0]}>
          <cylinderGeometry args={[0.06, 0.06, 2.8, 16]} />
          <meshStandardMaterial
            color="#b0b0b0"
            opacity={0.7}
            transparent
            metalness={0.4}
            roughness={0.5}
          />
        </mesh>
      )}

      {/* Position labels */}
      {position % 10 === 0 && (
        <Text
          position={[3.2, 0, 0]}
          fontSize={0.18}
          color={isMutation ? "#ff3366" : "#3c4f3d"}
          anchorX="left"
          font="/fonts/inter-bold.woff"
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
        <Canvas>
          <PerspectiveCamera makeDefault position={[8, 12, 8]} fov={60} />
          <OrbitControls
            enableZoom={true}
            enablePan={true}
            enableRotate={true}
            autoRotate={true}
            autoRotateSpeed={0.8}
            minDistance={5}
            maxDistance={30}
          />

          {/* Lighting */}
          <ambientLight intensity={0.8} />
          <directionalLight position={[10, 10, 5]} intensity={1} />
          <pointLight position={[-10, -10, -5]} intensity={0.5} color="#4488ff" />

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
