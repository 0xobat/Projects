"use client";

import { useRef, useMemo } from "react";
import { Canvas, useFrame } from "@react-three/fiber";
import * as THREE from "three";

const HEART_COUNT = 100;
const BURST_DURATION = 3; // seconds

function seededRandom(seed: number) {
  const x = Math.sin(seed + 1) * 10000;
  return x - Math.floor(x);
}

/** Create a 2D heart shape for extrusion into 3D */
function createHeartShape() {
  const shape = new THREE.Shape();
  const s = 0.15;
  shape.moveTo(0, 0);
  shape.bezierCurveTo(0, -s * 3, -s * 5, -s * 3, -s * 5, 0);
  shape.bezierCurveTo(-s * 5, s * 3.5, 0, s * 5.5, 0, s * 8);
  shape.bezierCurveTo(0, s * 5.5, s * 5, s * 3.5, s * 5, 0);
  shape.bezierCurveTo(s * 5, -s * 3, 0, -s * 3, 0, 0);
  return shape;
}

interface Particle {
  position: THREE.Vector3;
  velocity: THREE.Vector3;
  rotation: THREE.Euler;
  rotationSpeed: THREE.Vector3;
  scale: number;
  color: THREE.Color;
}

const COLORS = [
  new THREE.Color("#8b0a1a"), // deep crimson
  new THREE.Color("#c0192c"), // classic red
  new THREE.Color("#e8626c"), // coral red
  new THREE.Color("#d63560"), // rose
  new THREE.Color("#ec7793"), // medium pink
  new THREE.Color("#f4a9b8"), // soft pink
  new THREE.Color("#f7c5d0"), // blush pink
  new THREE.Color("#cc2d56"), // raspberry
];

function initParticles(): Particle[] {
  return Array.from({ length: HEART_COUNT }, (_, i) => {
    const seed = i * 7;
    const theta = seededRandom(seed) * Math.PI * 2;
    const phi = seededRandom(seed + 1) * Math.PI - Math.PI / 2;
    const speed = 3 + seededRandom(seed + 2) * 5;

    return {
      position: new THREE.Vector3(0, 0, 0),
      velocity: new THREE.Vector3(
        Math.cos(theta) * Math.cos(phi) * speed,
        Math.sin(phi) * speed * 0.8 + 2,
        Math.sin(theta) * Math.cos(phi) * speed * 0.5
      ),
      rotation: new THREE.Euler(
        seededRandom(seed + 3) * Math.PI * 2,
        seededRandom(seed + 4) * Math.PI * 2,
        seededRandom(seed + 5) * Math.PI * 2
      ),
      rotationSpeed: new THREE.Vector3(
        (seededRandom(seed + 6) - 0.5) * 6,
        (seededRandom(seed + 7) - 0.5) * 6,
        (seededRandom(seed + 8) - 0.5) * 6
      ),
      scale: 0.5 + seededRandom(seed + 9) * 1,
      color: COLORS[Math.floor(seededRandom(seed + 10) * COLORS.length)],
    };
  });
}

const _tempObject = new THREE.Object3D();
const _tempColor = new THREE.Color();

function HeartParticles({ onComplete }: { onComplete: () => void }) {
  const meshRef = useRef<THREE.InstancedMesh>(null);
  const particlesRef = useRef<Particle[] | null>(null);
  const elapsed = useRef(0);
  const completed = useRef(false);
  const colorsSet = useRef(false);

  if (particlesRef.current === null) {
    particlesRef.current = initParticles();
  }

  const geometry = useMemo(() => {
    const shape = createHeartShape();
    return new THREE.ExtrudeGeometry(shape, {
      depth: 0.15,
      bevelEnabled: true,
      bevelThickness: 0.04,
      bevelSize: 0.04,
      bevelSegments: 2,
    });
  }, []);

  useFrame((_, delta) => {
    const mesh = meshRef.current;
    const particles = particlesRef.current;
    if (!mesh || !particles) return;

    // Set colors on first frame
    if (!colorsSet.current) {
      colorsSet.current = true;
      for (let i = 0; i < HEART_COUNT; i++) {
        _tempColor.copy(particles[i].color);
        mesh.setColorAt(i, _tempColor);
      }
      if (mesh.instanceColor) mesh.instanceColor.needsUpdate = true;
    }

    elapsed.current += delta;
    const t = elapsed.current;
    const gravity = -6;

    for (let i = 0; i < HEART_COUNT; i++) {
      const p = particles[i];

      // Update position
      p.position.x += p.velocity.x * delta;
      p.position.y += p.velocity.y * delta;
      p.position.z += p.velocity.z * delta;

      // Apply gravity
      p.velocity.y += gravity * delta;

      // Apply drag
      p.velocity.x *= 0.995;
      p.velocity.z *= 0.995;

      // Update rotation
      p.rotation.x += p.rotationSpeed.x * delta;
      p.rotation.y += p.rotationSpeed.y * delta;
      p.rotation.z += p.rotationSpeed.z * delta;

      // Fade out near the end
      const fadeStart = BURST_DURATION * 0.6;
      const opacity = t > fadeStart ? 1 - (t - fadeStart) / (BURST_DURATION - fadeStart) : 1;
      const s = p.scale * Math.max(0, opacity);

      _tempObject.position.copy(p.position);
      _tempObject.rotation.copy(p.rotation);
      _tempObject.scale.setScalar(s);
      _tempObject.updateMatrix();
      mesh.setMatrixAt(i, _tempObject.matrix);
    }

    mesh.instanceMatrix.needsUpdate = true;

    if (t >= BURST_DURATION && !completed.current) {
      completed.current = true;
      onComplete();
    }
  });

  return (
    <instancedMesh ref={meshRef} args={[geometry, undefined, HEART_COUNT]}>
      <meshStandardMaterial
        vertexColors
        toneMapped={false}
        emissive="#ffffff"
        emissiveIntensity={0.4}
      />
    </instancedMesh>
  );
}

export default function HeartBurst({ onComplete }: { onComplete: () => void }) {
  return (
    <Canvas
      camera={{ position: [0, 0, 8], fov: 60 }}
      style={{ position: "absolute", inset: 0 }}
      gl={{ alpha: true, antialias: true }}
    >
      <ambientLight intensity={0.8} />
      <pointLight position={[5, 5, 5]} intensity={1.5} />
      <pointLight position={[-5, -5, 5]} intensity={0.5} color="#f4a9b8" />
      <HeartParticles onComplete={onComplete} />
    </Canvas>
  );
}
