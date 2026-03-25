# Unity 3D Prefab Creation Guide

**Goal:** Create 8 reusable machine prefabs using only Unity primitive 3D objects (Cubes, Cylinders, Spheres). These prefabs will be dynamically spawned by the `MachineSpawner` based on `factory_config.json`.

---

## 🏗️ General Setup for ALL Prefabs

1. Create an **Empty GameObject**, name it exactly as the prefab name (e.g., `lathe_machine`).
2. Set its Transform to Position (0,0,0), Rotation (0,0,0), Scale (1,1,1).
3. Add a **Box Collider** around the entire group (check "Is Trigger" if you want click events).
4. Add the `MachineVisual.cs` script to its root.
5. Create a Canvas -> TextMeshPro - Text as a child, set to World Space for the Queue display above the machine. Link this TMP reference in `MachineVisual.cs`.
6. Add an empty GameObject child named "BreakdownIndicator" (a red pulsing light/particle). Keep it disabled. Link in script.
7. Add an empty GameObject child named "BottleneckArrow" (a large yellow arrow pointing down). Link in script.
8. Drag the root GameObject into your `Assets/Resources/Prefabs` folder. (MUST BE EXACTLY THIS PATH).

---

## 🛠️ Lathe Factory Prefabs

### 1. `lathe_machine` (கடைசல் இயந்திரம்)
- **Base:** Cube (Scale 2, 0.5, 0.8), Color: Dark Grey.
- **Spindle:** Cylinder on the left side (Scale 0.4, 0.3, 0.4, rotate X 90), Color: Silver.
- **Tailstock:** Small Cube on the right (Scale 0.3, 0.4, 0.3), Color: Blue.
- **Operator Panel:** Small angled Cube on front (Scale 0.4, 0.3, 0.1), Color: Light Grey.

### 2. `cnc_mill` (சிஎன்சி மில்)
- **Base:** Large Cube (Scale 1.5, 2.0, 1.2), Color: Light Grey or White.
- **Window:** Thin Cube on the front (Scale 1.0, 0.8, 0.1), Color: Transparent Blue/Glass.
- **Spindle Head:** Cylinder inside (Scale 0.2, 0.5, 0.2), Color: Silver.
- **Control Arm:** Cube sticking out right (Scale 0.3, 0.3, 0.1), Color: Black.

### 3. `welding_station` (வெல்டிங் நிலையம்)
- **Table:** Low Cube (Scale 1.5, 0.1, 1.0) supported by 4 thin cylinders (legs).
- **Curtain/Shield:** Thin transparent red/yellow cube covering 3 sides.
- **Welding Arm:** Cylinder reaching from top right downwards. Color: Orange.

### 4. `surface_grinder` (மேற்பரப்பு சாணை)
- **Base:** Cube (Scale 1.2, 1.5, 1.0), Color: Green.
- **Grinding Wheel:** Thin Cylinder (Scale 0.6, 0.1, 0.6, rotate Z 90) hovering over table. Color: Dark Grey.
- **Magnetic Chuck:** Thin Cube underneath wheel (Scale 0.8, 0.1, 0.6), Color: Silver.

---

## 🧵 Textile Factory Prefabs

### 5. `spinning` (நூற்பு இயந்திரம்)
- **Frame:** Long tall Cube (Scale 3.0, 1.5, 0.5), Color: Light Blue.
- **Bobbins:** Multiple small Cylinders (Scale 0.1, 0.2, 0.1) stacked across the top, Color: White.

### 6. `loom` (நெசவு தறி)
- **Base:** Wide Cube (Scale 2.0, 1.0, 1.5), Color: Dark Green.
- **Warp Beam:** Long Cylinder at the back (Scale 0.4, 1.8, 0.4, rotate Z 90).
- **Fabric Roll:** Cylinder at the front (Scale 0.3, 1.8, 0.3, rotate Z 90), Color: White/Cloth.

### 7. `dyeing_vat` (சாயத் தொட்டி)
- **Tank:** Large Cylinder (Scale 1.5, 1.0, 1.5), Color: Stainless Steel.
- **Liquid Top:** Cylinder inside just below rim (Scale 1.4, 0.01, 1.4), Color: Bright Purple or Red.
- **Pipes:** Small cylinders connecting to the tank side.

### 8. `cutting` (வெட்டுதல்)
- **Long Table:** Very long Cube (Scale 4.0, 0.8, 1.5), Color: Beige/Wood or White.
- **Cutting Head:** Cube spanning the width of the table (Scale 0.2, 0.2, 1.6), Color: Yellow.
- **Fabric Layer:** Thin flat cube on top of table (Scale 3.8, 0.05, 1.4).

---

## 🎨 Materials & Colors
Create a generic Material for each base color (Grey, Blue, Green, White, Silver, Red) using standard Unity Standard/URP shader. Keep it simple for high performance.
