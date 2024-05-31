# Makefile
# See https://docs.cocotb.org/en/stable/quickstart.html for more info

# defaults
SIM ?= icarus
TOPLEVEL_LANG ?= verilog
SRC_DIR = $(PWD)/../src
PROJECT_SOURCES = \
	raybox-zero/src/rtl/fixed_point_params.v	\
	raybox-zero/src/rtl/helpers.v				\
	raybox-zero/src/rtl/debug_overlay.v			\
	raybox-zero/src/rtl/lzc.v					\
	raybox-zero/src/rtl/map_overlay.v			\
	raybox-zero/src/rtl/map_rom.v				\
	raybox-zero/src/rtl/pov.v					\
	raybox-zero/src/rtl/reciprocal.v			\
	raybox-zero/src/rtl/row_render.v			\
	raybox-zero/src/rtl/spi_registers.v			\
	raybox-zero/src/rtl/vga_mux.v				\
	raybox-zero/src/rtl/vga_sync.v				\
	raybox-zero/src/rtl/wall_tracer.v			\
	raybox-zero/src/rtl/rbzero.v				\
	raybox-zero/src/rtl/top_raybox_zero_fsm.v	\
	project.v

ifneq ($(GATES),yes)

# RTL simulation:
SIM_BUILD				= sim_build/rtl
VERILOG_SOURCES += $(addprefix $(SRC_DIR)/,$(PROJECT_SOURCES))
COMPILE_ARGS 		+= -I$(SRC_DIR)
# Extra include dir hacked in for raybox-zero submodule:
COMPILE_ARGS 		+= -I$(SRC_DIR)/raybox-zero/src/rtl

else

# Gate level simulation:
SIM_BUILD				= sim_build/gl
COMPILE_ARGS    += -DGL_TEST
COMPILE_ARGS    += -DFUNCTIONAL
COMPILE_ARGS    += -DUSE_POWER_PINS
COMPILE_ARGS    += -DSIM
COMPILE_ARGS    += -DUNIT_DELAY=\#1
VERILOG_SOURCES += $(PDK_ROOT)/sky130A/libs.ref/sky130_fd_sc_hd/verilog/primitives.v
VERILOG_SOURCES += $(PDK_ROOT)/sky130A/libs.ref/sky130_fd_sc_hd/verilog/sky130_fd_sc_hd.v

# this gets copied in by the GDS action workflow
VERILOG_SOURCES += $(PWD)/gate_level_netlist.v

endif

# Include the simulated SPI texture ROM:
VERILOG_SOURCES += $(PWD)/texture_rom/W25Q128JVxIM.v
# Include the testbench sources:
VERILOG_SOURCES += $(PWD)/tb.v 

TOPLEVEL = tb

# MODULE is the basename of the Python test file
MODULE = test

# include cocotb's make rules to take care of the simulator setup
include $(shell cocotb-config --makefiles)/Makefile.sim

clean_frames:
	rm -rf frames_out/*.ppm
	rm -rf frames_out/*.png

animate:
	./animate.sh --

wave:
	gtkwave tb.vcd tb.gtkw

