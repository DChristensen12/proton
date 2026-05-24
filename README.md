# PROTON

**P**hysics-informed **R**adiation **O**perator and **T**ime-series **O**ptimized **N**etwork.

A pipeline that starts from a real radiation sensor on the desk and
scales up to a distributed spatial mapping demo, with the laptop as the compute
hub. The phases are independent enough to build and test one at a time.

## What the hardware can actually do

The sensor is an FNIRSI GC-01 flashed with Rad Pro firmware. Rad Pro speaks a
request-response protocol over USB, not a continuous stream. You send a command,
it replies once. The full command set is documented at
https://github.com/Gissio/radpro/blob/main/docs/comm.md

The most important consequence for this project: there is no command that gives
you a timestamp for each individual pulse. The finest grained real time signal
is polling the cumulative pulse count. Genuine per-pulse arrival timing would
need a hardware tap on the tube pulse line, which is an optional add-on, not
part of the base kit. Phase 2 is written with that in mind.

## Layout

    proton/
      common/                     shared code used by every phase
        radpro_serial.py          the protocol wrapper, the foundation
        units.py                  counts to the five display units
      phase0_hardware/            flashing, verification, raw data access
        diagnostics/
          get_device_id.py        confirm the device is talking
          get_tube_sensitivity.py read the counts to dose constant
          probe_capabilities.py   inventory every supported command
          live_monitor.py         watch all units update in real time
          download_datalog.py     pull the on-device flash log to CSV
        config/
          device_config.py        device facts in one place
      phase1_pinn/                local PINN modeling
      phase2_diffusion/           generative inter-arrival modeling
      phase3_fno/                 distributed FNO mesh
    data/
      raw/  processed/  logs/
    notebooks/
    tests/

## Getting started, Phase 0

1. Flash Rad Pro on the GC-01 and toggle Data Mode ON in settings. Note that
   the flashing step itself wants a Windows machine per the Rad Pro install
   guide, even though everything after runs fine on Linux.
2. Plug in with a real data cable, not a charge-only one.
3. Install dependencies:

       pip install -r requirements.txt

4. Confirm the link:

       python proton/phase0_hardware/diagnostics/get_device_id.py

5. Read the sensitivity, which everything downstream depends on:

       python proton/phase0_hardware/diagnostics/get_tube_sensitivity.py --port /dev/ttyACM0

6. Inventory everything the device supports:

       python proton/phase0_hardware/diagnostics/probe_capabilities.py --port /dev/ttyACM0

Run the scripts from the project root so the imports resolve.

This project is a work in progress and will be updated throughout the year! Stay tuned!
