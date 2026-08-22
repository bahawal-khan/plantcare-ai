"use client";

import { useEffect, useRef, useState } from "react";
import type { Visualization3D } from "@/lib/types";
import { ExpandIcon } from "@/components/ui/icons";

type ViewerStatus = "loading" | "ready" | "error";

function hasWebGL(): boolean {
  try {
    const canvas = document.createElement("canvas");
    return Boolean(
      window.WebGLRenderingContext &&
        (canvas.getContext("webgl") || canvas.getContext("experimental-webgl")),
    );
  } catch {
    return false;
  }
}

export function GradCam3D({ visualization }: { visualization: Visualization3D }) {
  const containerRef = useRef<HTMLDivElement>(null);
  const wrapperRef = useRef<HTMLDivElement>(null);
  const [status, setStatus] = useState<ViewerStatus>("loading");
  const [isFullscreen, setIsFullscreen] = useState(false);

  // Chrome-only: tracks native fullscreen state. Independent of the WebGL
  // scene effect below -- toggling fullscreen never touches the three.js
  // renderer/camera/controls lifecycle.
  useEffect(() => {
    function handleChange() {
      setIsFullscreen(document.fullscreenElement === wrapperRef.current);
    }
    document.addEventListener("fullscreenchange", handleChange);
    return () => document.removeEventListener("fullscreenchange", handleChange);
  }, []);

  function toggleFullscreen() {
    if (!wrapperRef.current) return;
    if (document.fullscreenElement) {
      document.exitFullscreen();
    } else {
      wrapperRef.current.requestFullscreen?.();
    }
  }

  useEffect(() => {
    const container = containerRef.current;
    if (!container) return;

    let renderer: import("three").WebGLRenderer | undefined;
    let controls: import("three/examples/jsm/controls/OrbitControls.js").OrbitControls | undefined;
    let frameId = 0;
    let disposed = false;
    let resizeObserver: ResizeObserver | undefined;

    (async () => {
      if (!hasWebGL()) {
        setStatus("error");
        return;
      }
      try {
        const THREE = await import("three");
        const { OrbitControls } = await import("three/examples/jsm/controls/OrbitControls.js");

        if (disposed || !container) return;

        const [gridWidth, gridHeight] = visualization.grid_size;
        const heightmap = visualization.heightmap;

        const width = container.clientWidth || 320;
        const height = container.clientHeight || 320;

        const scene = new THREE.Scene();
        scene.background = new THREE.Color(0xffffff);
        scene.fog = new THREE.Fog(0xffffff, 4.5, 9);

        const camera = new THREE.PerspectiveCamera(45, width / height, 0.1, 100);
        camera.position.set(0, 2.6, 3.4);

        renderer = new THREE.WebGLRenderer({ antialias: true, alpha: false });
        renderer.setPixelRatio(Math.min(window.devicePixelRatio, 2));
        renderer.setSize(width, height);
        container.innerHTML = "";
        container.appendChild(renderer.domElement);

        // Grid floor for spatial reference against the white background, tinted
        // toward the brand's sage-green neutral rather than a generic engineering gray.
        const grid = new THREE.GridHelper(4, 20, 0xa9bab0, 0xe4e9e6);
        grid.position.y = -0.01;
        (grid.material as import("three").Material).transparent = true;
        (grid.material as import("three").Material).opacity = 0.8;
        scene.add(grid);

        const hemisphere = new THREE.HemisphereLight(0xffffff, 0xd7ded9, 0.95);
        const directional = new THREE.DirectionalLight(0xffffff, 0.9);
        directional.position.set(2, 3, 2);
        scene.add(hemisphere, directional);

        const geometry = new THREE.PlaneGeometry(3, 3, gridWidth - 1, gridHeight - 1);
        geometry.rotateX(-Math.PI / 2);

        const positions = geometry.attributes.position;
        const HEIGHT_SCALE = 0.6;
        for (let row = 0; row < gridHeight; row++) {
          for (let col = 0; col < gridWidth; col++) {
            const vertexIndex = row * gridWidth + col;
            const intensity = heightmap[row]?.[col] ?? 0;
            positions.setY(vertexIndex, intensity * HEIGHT_SCALE);
          }
        }
        positions.needsUpdate = true;
        geometry.computeVertexNormals();

        const texture = new THREE.TextureLoader().load(
          `data:image/png;base64,${visualization.texture_png_base64}`,
        );
        texture.colorSpace = THREE.SRGBColorSpace;

        const material = new THREE.MeshStandardMaterial({
          map: texture,
          roughness: 0.85,
          metalness: 0.05,
          side: THREE.DoubleSide,
        });

        const mesh = new THREE.Mesh(geometry, material);
        scene.add(mesh);

        controls = new OrbitControls(camera, renderer.domElement);
        controls.enableDamping = true;
        controls.dampingFactor = 0.08;
        controls.minDistance = 1.5;
        controls.maxDistance = 7;
        controls.autoRotate = true;
        controls.autoRotateSpeed = 1.2;

        const animate = () => {
          if (disposed) return;
          controls?.update();
          if (renderer) renderer.render(scene, camera);
          frameId = requestAnimationFrame(animate);
        };
        animate();

        resizeObserver = new ResizeObserver(() => {
          if (!container || !renderer) return;
          const w = container.clientWidth || width;
          const h = container.clientHeight || height;
          renderer.setSize(w, h);
          camera.aspect = w / h;
          camera.updateProjectionMatrix();
        });
        resizeObserver.observe(container);

        if (!disposed) setStatus("ready");

        return () => {
          cancelAnimationFrame(frameId);
          resizeObserver?.disconnect();
          controls?.dispose();
          geometry.dispose();
          material.dispose();
          texture.dispose();
          grid.geometry.dispose();
          (grid.material as import("three").Material).dispose();
          renderer?.dispose();
        };
      } catch {
        if (!disposed) setStatus("error");
      }
    })();

    return () => {
      disposed = true;
      cancelAnimationFrame(frameId);
      resizeObserver?.disconnect();
      controls?.dispose();
      renderer?.dispose();
      if (container) container.innerHTML = "";
    };
  }, [visualization]);

  if (status === "error") {
    return (
      <div className="flex h-56 flex-col items-center justify-center gap-2 rounded-2xl border border-border-default bg-surface-muted p-6 text-center sm:h-72">
        <p className="font-semibold text-text-strong">3D visualization unavailable</p>
        <p className="max-w-xs text-sm text-text-muted">
          Your browser or device doesn&apos;t support interactive 3D rendering. The standard 2D
          Grad-CAM heatmap above still shows the same AI attention regions.
        </p>
      </div>
    );
  }

  return (
    <div
      ref={wrapperRef}
      className={`relative overflow-hidden rounded-2xl border border-border-default ${
        isFullscreen ? "h-screen" : "h-56 sm:h-72"
      }`}
    >
      {status === "loading" && (
        <div className="absolute inset-0 z-10 flex items-center justify-center bg-white/95">
          <div className="flex items-center gap-3 text-ink-900/70">
            <span className="h-4 w-4 animate-spin rounded-full border-2 border-ink-900/20 border-t-brand-600" />
            <span className="text-sm">Loading 3D visualization&hellip;</span>
          </div>
        </div>
      )}
      <div ref={containerRef} className="h-full w-full" />
      {status === "ready" && (
        <>
          <div className="pointer-events-none absolute bottom-3 left-1/2 -translate-x-1/2 rounded-full bg-black/50 px-3 py-1 text-xs text-white/80">
            Drag to rotate &middot; Scroll to zoom
          </div>
          <button
            type="button"
            onClick={toggleFullscreen}
            aria-label={isFullscreen ? "Exit fullscreen" : "View fullscreen"}
            className="absolute right-3 top-3 flex h-9 w-9 items-center justify-center rounded-full bg-black/50 text-white/80 transition-colors hover:bg-black/70 hover:text-white"
          >
            <ExpandIcon className="h-4 w-4" />
          </button>
        </>
      )}
    </div>
  );
}
