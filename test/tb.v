`default_nettype none
`timescale 1ns / 1ps

/* This testbench just instantiates the module and makes some convenient wires
   that can be driven / tested by the cocotb test.py.
*/
module tb ();

  //NOTE: DON'T write VCD file, because it'd be huge!
  // // Dump the signals to a VCD file. You can view it with gtkwave.
  // initial begin
  //   $dumpfile("tb.vcd");
  //   $dumpvars(0, tb);
  //   #1;
  // end

  // --- Named inputs controlled by test: ---
  // Universal TT07 inputs:
  reg clk;
  reg rst_n;
  reg ena;
  // Specific inputs for raybox-zero:
  reg pov_sclk;
  reg pov_mosi;
  reg pov_ss_n;
  reg debug;
  reg inc_px;
  reg inc_py;
  reg registered_outputs; // aka just 'reg'
  reg reg_sclk;
  reg reg_mosi;
  reg reg_ss_n;
  // Specific outputs for raybox-zero:
  wire [5:0] rgb  = uo_out[7:2]; // B=[5:4], G=[3:2], R=[1:0]
  wire [1:0] rr = rgb[1:0];
  wire [1:0] gg = rgb[3:2];
  wire [1:0] bb = rgb[5:4];
  wire hsync_n    = uo_out[0];
  wire vsync_n    = uo_out[1];
  wire o_hblank   = uio_out[0];
  wire o_vblank   = uio_out[1];

  // --- DUT's generic IOs from the TT wrapper ---
  wire [7:0] ui_in;       // Dedicated inputs
  wire [7:0] uo_out;      // Dedicated outputs
  wire [7:0] uio_in;      // Bidir IOs: Input path
  wire [7:0] uio_out;     // Bidir IOs: Output path
  wire [7:0] uio_oe;      // Bidir IOs: Enable path (active high: 0=input, 1=output).

  assign ui_in = {
    1'b0,
    registered_outputs,
    inc_py,
    inc_px,
    debug,
    pov_ss_n,
    pov_mosi,
    pov_sclk
  };

  assign uio_in = {
    3'b000,
    reg_ss_n,
    reg_mosi,
    reg_sclk,
    2'b00
  };

  tt_um_algofoogle_raybox_zero user_project (

      // Include power ports for the Gate Level test:
`ifdef GL_TEST
      .VPWR(1'b1),
      .VGND(1'b0),
`endif

      .ui_in  (ui_in),    // Dedicated inputs
      .uo_out (uo_out),   // Dedicated outputs
      .uio_in (uio_in),   // IOs: Input path
      .uio_out(uio_out),  // IOs: Output path
      .uio_oe (uio_oe),   // IOs: Enable path (active high: 0=input, 1=output)
      .ena    (ena),      // enable - goes high when design is selected
      .clk    (clk),      // clock
      .rst_n  (rst_n)     // not reset
  );

endmodule
