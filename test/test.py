# SPDX-FileCopyrightText: © 2024 Anton Maurovic
# SPDX-License-Identifier: MIT

import cocotb
from cocotb.clock import Clock
from cocotb.triggers import RisingEdge, Timer, ClockCycles
import time
from os import environ as env
import re

HIGH_RES        = float(env.get('HIGH_RES')) if 'HIGH_RES' in env else None # If not None, scale H res by this, and step by CLOCK_PERIOD/HIGH_RES instead of unit clock cycles.
CLOCK_PERIOD    = float(env.get('CLOCK_PERIOD') or 40.0) # Default 40.0 (period of clk oscillator input, in nanoseconds)
FRAMES          = int(env.get('FRAMES')         or 3) # Default 3 (total frames to render)
INC_PX          = int(env.get('INC_PX')         or 1) # Default 1 (inc_px on)
INC_PY          = int(env.get('INC_PY')         or 1) # Default 1 (inc_py on)
GEN_TEX         = int(env.get('GEN_TEX')        or 0) # Default 0 (use tex ROM; no generated textures)
DEBUG_VEC       = int(env.get('DEBUG_VEC')      or 1) # Default 1 (show vectors debug)
REG             = int(env.get('REG')            or 0) # Default 0 (UNregistered outputs)

print(f"""
Test parameters (can be overridden using ENV vars):
---     HIGH_RES: {HIGH_RES}
--- CLOCK_PERIOD: {CLOCK_PERIOD}
---       FRAMES: {FRAMES}
---       INC_PX: {INC_PX}
---       INC_PY: {INC_PY}
---      GEN_TEX: {GEN_TEX}
---    DEBUG_VEC: {DEBUG_VEC}
---          REG: {REG}
""")

# Make sure all bidir pins are configured as they should be,
# for this design:
def check_uio_out(dut):
    # Make sure 2 LSB are outputs,
    # and all but [5] (bidir) of the rest are inputs:
    assert re.match('00.00011', dut.uio_oe.value.binstr)

# This can represent hard-wired stuff:
def set_default_start_state(dut):
    dut.ena.value                   = 1
    # POV SPI interface inactive:
    dut.pov_sclk.value              = 1
    dut.pov_mosi.value              = 1
    dut.pov_ss_n.value              = 1
    # REG SPI interface also inactive:
    dut.reg_sclk.value              = 1
    dut.reg_mosi.value              = 1
    dut.reg_ss_n.value              = 1
    # Enable debug display on-screen:
    dut.debug.value                 = DEBUG_VEC
    # Enable demo mode (player position auto-increment):
    dut.inc_px.value                = INC_PX
    dut.inc_py.value                = INC_PY
    # Use generated textures instead of external texture SPI memory:
    dut.gen_tex.value               = GEN_TEX
    # Present UNregistered outputs:
    dut.registered_outputs.value    = REG

@cocotb.test()
async def test_frames(dut):
    """
    Generate a number of full video frames and write to rbz_basic_frame-###.ppm
    """

    dut._log.info("Starting test_frames...")

    frame_count = FRAMES # No. of frames to render.
    hrange = 800
    frame_height = 525
    vrange = frame_height
    hres = HIGH_RES or 1

    print(f"Rendering {frame_count} full frame(s)...")

    set_default_start_state(dut)
    # Start with reset released:
    dut.rst_n.value = 1

    clk = Clock(dut.clk, CLOCK_PERIOD, units="ns")
    cocotb.start_soon(clk.start())

    # Wait 3 clocks...
    await ClockCycles(dut.clk, 3)
    check_uio_out(dut)
    dut._log.info("Assert reset...")
    # ...then assert reset:
    dut.rst_n.value = 0
    # ...and wait another 10 clocks...
    await ClockCycles(dut.clk, 10)
    check_uio_out(dut)
    dut._log.info("Release reset...")
    # ...then release reset:
    dut.rst_n.value = 1
    x_count = 0 # Counts unknown signal values.
    z_count = 0
    sample_count = 0 # Total count of pixels or samples.

    for frame in range(frame_count):
        render_start_time = time.time()
        # Create PPM file to visualise the frame, and write its header:
        img = open(f"frames_out/rbz_basic_frame-{frame:03d}.ppm", "w")
        img.write("P3\n")
        img.write(f"{int(hrange*hres)} {vrange:d}\n")
        img.write("255\n")

        for n in range(vrange): # 525 lines * however many frames in frame_count
            print(f"Rendering line {n} of frame {frame}")
            for n in range(int(hrange*hres)): # 800 pixel clocks per line.
                if n % 100 == 0:
                    print('.', end='')
                if 'x' in dut.rgb.value.binstr:
                    # Output is unknown; make it green:
                    r = 0
                    g = 255
                    b = 0
                elif 'z' in dut.rgb.value.binstr:
                    # Output is HiZ; make it magenta:
                    r = 255
                    g = 0
                    b = 255
                else:
                    rr = dut.rr.value
                    gg = dut.gg.value
                    bb = dut.bb.value
                    hsyncb = 255 if dut.hsync_n.value.binstr=='x' else (0==dut.hsync_n.value)*0b110000
                    vsyncb = 128 if dut.vsync_n.value.binstr=='x' else (0==dut.vsync_n.value)*0b110000
                    r = (rr << 6) | hsyncb
                    g = (gg << 6) | vsyncb
                    b = (bb << 6)
                sample_count += 1
                if 'x' in (dut.rgb.value.binstr + dut.hsync_n.value.binstr + dut.vsync_n.value.binstr):
                    x_count += 1
                if 'z' in (dut.rgb.value.binstr + dut.hsync_n.value.binstr + dut.vsync_n.value.binstr):
                    z_count += 1
                img.write(f"{r} {g} {b}\n")
                if HIGH_RES is None:
                    await ClockCycles(dut.clk, 1) 
                else:
                    await Timer(CLOCK_PERIOD/hres, units='ns')
        img.close()
        render_stop_time = time.time()
        delta = render_stop_time - render_start_time
        print(f"[{render_stop_time}: Frame simulated in {delta} seconds]")
    print("Waiting 1 more clock, for start of next line...")
    await ClockCycles(dut.clk, 1)
    print(f"DONE: Out of {sample_count} pixels/samples, got: {x_count} 'x'; {z_count} 'z'")

