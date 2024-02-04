VERILOG_INCLUDE_DIRS = $(PWD)/include
VERILOG_SOURCES = $(PWD)/scr1_pipe_ialu.sv 
TOPLEVEL=scr1_pipe_ialu  
MODULE=test 

EXTRA_ARGS += --trace --trace-structs
EXTRA_ARGS = --coverage --error-limit 0
VERILATOR_FLAGS += --cc --exe --error-limit 0
include $(shell cocotb-config --makefiles)/Makefile.sim



report:
	verilator_coverage  -write-info coverage.info coverage.dat
	genhtml coverage.info --output-directory coverage
	

