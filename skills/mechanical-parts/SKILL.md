---
name: mechanical-parts
description: Create mechanical and industrial parts — threads, fasteners, bearings, sprockets, flanges, pipes, and OpenBuilds CNC components. Use when the user wants threaded parts, bolts, nuts, gears, bearings, or linear motion components.
---

# Mechanical Parts

Help the user create mechanical and industrial components using bd_warehouse's parametric part library.

## Workflow

1. Clarify the user's need — what part, what size, what it mates with
2. Select the right tool and parameters (see categories below)
3. Call the appropriate tool to generate the part
4. Call `measure_model` to verify dimensions
5. Call `analyze_printability` to check for FDM issues
6. If creating mating parts (e.g. bolt + nut, male + female thread), create both

## Threads

Use `create_thread` for threaded shafts, bores, bottle necks, lead screws.

- **ISO metric** (`thread_type="iso"`): Standard M-series bolts/nuts. Specify `major_diameter` and `pitch` in mm.
  - Common: M3x0.5, M4x0.7, M5x0.8, M6x1.0, M8x1.25, M10x1.5
  - Set `external=True` for bolt shaft, `external=False` for nut bore
- **ACME** (`thread_type="acme"`): Power screws, vises, clamps. Imperial sizes via `size` ("3/8", "1/2", "1").
- **Metric trapezoidal** (`thread_type="metric_trapezoidal"`): Lead screws, linear actuators. Sizes via `size` ("10x2", "20x4").
- **Plastic bottle** (`thread_type="plastic_bottle"`): Jar lids, bottle caps. Sizes via `size` ("L38SP400").
  - Use `manufacturing_compensation=0.2` for FDM printing tolerance

### Mating Thread Pairs

Always create both male and female parts when designing threaded assemblies:
```
1. create_thread(name="bolt_shaft", thread_type="iso", major_diameter=10, pitch=1.5, length=20, external=True)
2. create_thread(name="nut_bore", thread_type="iso", major_diameter=10, pitch=1.5, length=10, external=False)
```

## Fasteners

Use `create_fastener` for standard hardware with real geometry.

- **Screws**: socket_head_cap_screw, hex_head_screw, button_head_screw, counter_sunk_screw, pan_head_screw, set_screw, low_profile_screw
- **Nuts**: hex_nut, hex_nut_with_flange, square_nut, domed_cap_nut
- **Washers**: plain_washer, chamfered_washer
- **Inserts**: heat_set_nut (with McMaster-Carr or Hilitchi sizing)

Sizes use ISO format: "M3-0.5", "M5-0.8", "M8-1.25". Heat-set nuts add length: "M3-0.5-Standard".

## Bearings

Use `create_bearing` for standard ball and roller bearings.

- Types: deep_groove_ball, capped_deep_groove_ball, angular_contact_ball, cylindrical_roller, tapered_roller
- Sizes: "M8-22-7" = 8mm bore, 22mm OD, 7mm width
- Use to design bearing housings — create the bearing, measure it, then design the pocket

## Sprockets

Use `create_sprocket` for chain drive mechanisms.

- Default: ANSI #40 chain (12.7mm pitch, 7.9375mm roller)
- Key params: `num_teeth`, `bore_diameter`, optional mounting bolt pattern
- For ANSI #25: chain_pitch=6.35, roller_diameter=3.302
- For ANSI #60: chain_pitch=19.05, roller_diameter=11.91

## Flanges

Use `create_flange` for pipe flanges (ASME B16.5).

- Types: blind, slip_on, weld_neck, lapped, socket_weld
- NPS sizes: "1/2" through "24"
- Classes: 150, 300, 400, 600, 900, 1500, 2500

## Pipes

Use `create_pipe` for custom tube/pipe sections.

- Specify outer_diameter, wall_thickness, and length in mm
- Combine with `create_thread` to add threaded ends

## OpenBuilds CNC Parts

Use `create_openbuilds_part` for CNC/linear motion reference parts.

- v_slot_rail: V-Slot extrusion profiles (20x20, 20x40, etc.)
- c_beam_rail: C-Beam linear rail
- lead_screw: 8mm metric lead screw with trapezoidal thread

## FDM Printing Tips

- Threads: Print vertically (thread axis = Z). Use 0.1-0.15mm layer height for fine threads.
- Clearance: Add 0.2-0.3mm to female thread `manufacturing_compensation` for FDM
- Bearings: Print bearing housings, not bearings themselves (use real bearings)
- Sprockets: Print flat on bed. Use 100% infill for load-bearing sprockets.
- Fasteners: Reference parts for designing around — use real hardware in assemblies
