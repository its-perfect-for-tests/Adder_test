import cocotb
from cocotb.clock import Clock
from cocotb.triggers import Timer, RisingEdge

Z_FLAG = 0b1000
S_FLAG = 0b0100
O_FLAG = 0b0010
C_FLAG = 0b0001
ADD_CMD = 4
SUB_CMD = 5

MAX = 2**31 - 1
MIN = -(2**31)


def cast_pos_to_neg(x):
    return (x - (2**32))


@cocotb.test()
async def simple_adder_test(dut):
    dut._log.info("Running simple adder test!")
    c = Clock(dut.clk, 10, 'ns')
    await cocotb.start(c.start())
    a = 1
    b = 2
    for cycle in range(10):
        a += 1
        b += 1
        await RisingEdge(dut.clk)
        dut.exu2ialu_main_op1_i <= a
        dut.exu2ialu_main_op2_i <= b
        dut.exu2ialu_cmd_i <= ADD_CMD
        await RisingEdge(dut.clk)
        assert dut.ialu2exu_main_res_o == (a+b)
        assert dut.main_sum_pos_ovflw == 0
        assert dut.main_sum_neg_ovflw == 0
        assert dut.main_sum_flags == 0
        assert dut.main_sum_neg_ovflw == 0
        assert dut.main_sum_pos_ovflw == 0


@cocotb.test()
async def adder_limit_test(dut):
    dut._log.info("Running limit test!")
    c = Clock(dut.clk, 10, 'ns')
    await cocotb.start(c.start())

    # check a + b = 2^32 - 1
    a = 2**30
    b = MAX - a
    await RisingEdge(dut.clk)
    dut.exu2ialu_main_op1_i <= a
    dut.exu2ialu_main_op2_i <= b
    dut.exu2ialu_cmd_i <= ADD_CMD
    await RisingEdge(dut.clk)

    assert dut.ialu2exu_main_res_o == (
        a+b), f"a = {a}, b = {b}, res = {dut.ialu2exu_main_res_o}"
    assert dut.main_sum_flags == (
        0), f"dut.main_sum_flags = {dut.main_sum_flags }"
    assert dut.main_sum_neg_ovflw == 0
    assert dut.main_sum_pos_ovflw == 0

    # check 0 + 0 = 0
    a = 0
    b = 0
    await RisingEdge(dut.clk)
    dut.exu2ialu_main_op1_i <= a
    dut.exu2ialu_main_op2_i <= b
    dut.exu2ialu_cmd_i <= ADD_CMD
    await RisingEdge(dut.clk)

    assert dut.ialu2exu_main_res_o == (
        a+b), f"a = {a}, b = {b}, res = {dut.ialu2exu_main_res_o}"
    assert dut.main_sum_flags == (
        Z_FLAG), f"dut.main_sum_flags = {dut.main_sum_flags }"
    assert dut.main_sum_neg_ovflw == 0
    assert dut.main_sum_pos_ovflw == 0

    # check (-1) + 1 = 0
    a = -1
    b = 1
    await RisingEdge(dut.clk)
    dut.exu2ialu_main_op1_i <= a
    dut.exu2ialu_main_op2_i <= b
    dut.exu2ialu_cmd_i <= ADD_CMD
    await RisingEdge(dut.clk)

    assert dut.ialu2exu_main_res_o == (
        a+b), f"a = {a}, b = {b}, res = {dut.ialu2exu_main_res_o}"
    assert dut.main_sum_flags == (
        Z_FLAG | O_FLAG | C_FLAG), f"dut.main_sum_flags = {dut.main_sum_flags }"
    assert dut.main_sum_neg_ovflw == 1
    assert dut.main_sum_pos_ovflw == 0

    a = 1
    b = -2
    await RisingEdge(dut.clk)
    dut.exu2ialu_main_op1_i <= a
    dut.exu2ialu_main_op2_i <= b
    dut.exu2ialu_cmd_i <= ADD_CMD
    await RisingEdge(dut.clk)

    res = cast_pos_to_neg(int(dut.ialu2exu_main_res_o))
    assert res == (
        a+b), f"a = {a}, b = {b}, res = {res}"
    assert dut.main_sum_flags == (
        S_FLAG | O_FLAG), f"dut.main_sum_flags = {dut.main_sum_flags }"
    assert dut.main_sum_neg_ovflw == 0
    assert dut.main_sum_pos_ovflw == 1

    # check -(2^31) + 0
    a = MIN
    b = 0
    await RisingEdge(dut.clk)
    dut.exu2ialu_main_op1_i <= a
    dut.exu2ialu_main_op2_i <= b
    dut.exu2ialu_cmd_i <= ADD_CMD
    await RisingEdge(dut.clk)
    res_neg = cast_pos_to_neg(int(dut.ialu2exu_main_res_o))

    assert res_neg == (
        a+b), f"a = {a}, b = {b}, res = {res_neg}"
    assert dut.main_sum_flags == (
        S_FLAG), f"dut.main_sum_flags = {dut.main_sum_flags }"
    assert dut.main_sum_neg_ovflw == 0
    assert dut.main_sum_pos_ovflw == 0


@cocotb.test()
async def adder_negtive_test(dut):
    dut._log.info("Running adder negative test!")
    c = Clock(dut.clk, 10, 'ns')
    await cocotb.start(c.start())
    a = -1
    b = -1
    await RisingEdge(dut.clk)
    dut.exu2ialu_main_op1_i <= a
    dut.exu2ialu_main_op2_i <= b
    dut.exu2ialu_cmd_i <= ADD_CMD
    await RisingEdge(dut.clk)
    res_neg = cast_pos_to_neg(int(dut.ialu2exu_main_res_o))

    assert res_neg == (
        a+b), f"a = {a}, b = {b}, res = {res_neg}"
    assert dut.main_sum_flags == (
        C_FLAG | S_FLAG), f"dut.main_sum_flags = {dut.main_sum_flags }"
    assert dut.main_sum_neg_ovflw == 0
    assert dut.main_sum_pos_ovflw == 0

    a = -5
    b = -50
    await RisingEdge(dut.clk)
    dut.exu2ialu_main_op1_i <= a
    dut.exu2ialu_main_op2_i <= b
    dut.exu2ialu_cmd_i <= ADD_CMD
    await RisingEdge(dut.clk)
    res_neg = cast_pos_to_neg(int(dut.ialu2exu_main_res_o))

    assert res_neg == (
        a+b), f"a = {a}, b = {b}, res = {res_neg}"
    assert dut.main_sum_flags == (
        C_FLAG | S_FLAG), f"dut.main_sum_flags = {dut.main_sum_flags }"
    assert dut.main_sum_neg_ovflw == 0
    assert dut.main_sum_pos_ovflw == 0


@cocotb.test()
async def adder_overflow_test(dut):
    dut._log.info("Running adder overflow test!")
    c = Clock(dut.clk, 10, 'ns')
    await cocotb.start(c.start())
    a = MIN
    b = -1
    await RisingEdge(dut.clk)
    dut.exu2ialu_main_op1_i <= a
    dut.exu2ialu_main_op2_i <= b
    dut.exu2ialu_cmd_i <= ADD_CMD
    await RisingEdge(dut.clk)
    print(a+b)
    res_neg = cast_pos_to_neg(int(dut.ialu2exu_main_res_o))
    assert res_neg == (
        a+b), f"a = {a}, b = {b}, res = {res_neg}"
    assert dut.main_sum_flags == (
        C_FLAG), f"dut.main_sum_flags = {dut.main_sum_flags }"
    assert dut.main_sum_neg_ovflw == 0
    assert dut.main_sum_pos_ovflw == 0

    a = MAX
    b = 1
    await RisingEdge(dut.clk)
    dut.exu2ialu_main_op1_i <= a
    dut.exu2ialu_main_op2_i <= b
    dut.exu2ialu_cmd_i <= ADD_CMD
    await RisingEdge(dut.clk)
    res = int(dut.ialu2exu_main_res_o)
    assert res == (
        a+b), f"a = {a}, b = {b}, res = {res}"
    assert dut.main_sum_flags == (
        S_FLAG), f"dut.main_sum_flags = {dut.main_sum_flags }"
    assert dut.main_sum_neg_ovflw == 0
    assert dut.main_sum_pos_ovflw == 0

    a = 2 ** 32 - 1
    b = 1
    await RisingEdge(dut.clk)
    dut.exu2ialu_main_op1_i <= a
    dut.exu2ialu_main_op2_i <= b
    dut.exu2ialu_cmd_i <= ADD_CMD
    await RisingEdge(dut.clk)
    res = int(dut.ialu2exu_main_res_o)

    assert res == 0, f"a = {a}, b = {b}, res = {res}"
    assert dut.main_sum_flags == (
        O_FLAG | Z_FLAG | C_FLAG), f"dut.main_sum_flags = {dut.main_sum_flags }"
    assert dut.main_sum_neg_ovflw == 1
    assert dut.main_sum_pos_ovflw == 0


@cocotb.test()
async def simple_sub_test(dut):
    dut._log.info("Running simple sub test!")
    c = Clock(dut.clk, 10, 'ns')
    await cocotb.start(c.start())
    b = 1
    a = 2
    for cycle in range(10):
        a += 1
        b += 1
        await RisingEdge(dut.clk)
        dut.exu2ialu_main_op1_i <= a
        dut.exu2ialu_main_op2_i <= b
        dut.exu2ialu_cmd_i <= SUB_CMD
        await RisingEdge(dut.clk)
        assert dut.ialu2exu_main_res_o == (a-b)
        assert dut.main_sum_pos_ovflw == 0
        assert dut.main_sum_neg_ovflw == 0
        assert dut.main_sum_flags == 0
        assert dut.main_sum_neg_ovflw == 0
        assert dut.main_sum_pos_ovflw == 0
    b = 2
    a = 1
    for cycle in range(10):
        b += 1
        await RisingEdge(dut.clk)
        dut.exu2ialu_main_op1_i <= a
        dut.exu2ialu_main_op2_i <= b
        dut.exu2ialu_cmd_i <= SUB_CMD
        await RisingEdge(dut.clk)
        res = cast_pos_to_neg(int(dut.ialu2exu_main_res_o))
        assert res == (a-b)
        assert dut.main_sum_pos_ovflw == 0
        assert dut.main_sum_neg_ovflw == 0
        assert dut.main_sum_flags == S_FLAG | C_FLAG, f"dut.main_sum_flags = {dut.main_sum_flags}, a = {a}, b = {b}"
        assert dut.main_sum_neg_ovflw == 0
        assert dut.main_sum_pos_ovflw == 0


@cocotb.test()
async def sub_limit_test(dut):
    dut._log.info("Running limit test!")
    c = Clock(dut.clk, 10, 'ns')
    await cocotb.start(c.start())

    # check a + b = 2^32 - 1
    a = MIN + 1
    b = 1
    await RisingEdge(dut.clk)
    dut.exu2ialu_main_op1_i <= a
    dut.exu2ialu_main_op2_i <= b
    dut.exu2ialu_cmd_i <= SUB_CMD
    await RisingEdge(dut.clk)

    res = cast_pos_to_neg(int(dut.ialu2exu_main_res_o))
    assert res == (
        a-b), f"a = {a}, b = {b}, res = {res}"
    assert dut.main_sum_flags == (
        S_FLAG), f"dut.main_sum_flags = {dut.main_sum_flags }"
    assert dut.main_sum_neg_ovflw == 0
    assert dut.main_sum_pos_ovflw == 0

    a = MIN
    b = 1
    await RisingEdge(dut.clk)
    dut.exu2ialu_main_op1_i <= a
    dut.exu2ialu_main_op2_i <= b
    dut.exu2ialu_cmd_i <= SUB_CMD
    await RisingEdge(dut.clk)

    res = cast_pos_to_neg(int(dut.ialu2exu_main_res_o))
    assert res == (
        a-b), f"a = {a}, b = {b}, res = {res}"
    assert dut.main_sum_flags == (
        O_FLAG), f"dut.main_sum_flags = {dut.main_sum_flags }"
    assert dut.main_sum_neg_ovflw == 1
    assert dut.main_sum_pos_ovflw == 0

    a = MIN
    b = MIN
    await RisingEdge(dut.clk)
    dut.exu2ialu_main_op1_i <= a
    dut.exu2ialu_main_op2_i <= b
    dut.exu2ialu_cmd_i <= SUB_CMD
    await RisingEdge(dut.clk)

    res = int(dut.ialu2exu_main_res_o)
    assert res == (
        0), f"a = {a}, b = {b}, res = {res}"
    assert dut.main_sum_flags == (
        Z_FLAG), f"dut.main_sum_flags = {dut.main_sum_flags }"
    assert dut.main_sum_neg_ovflw == 0
    assert dut.main_sum_pos_ovflw == 0

    a = MAX
    b = MAX
    await RisingEdge(dut.clk)
    dut.exu2ialu_main_op1_i <= a
    dut.exu2ialu_main_op2_i <= b
    dut.exu2ialu_cmd_i <= SUB_CMD
    await RisingEdge(dut.clk)

    res = int(dut.ialu2exu_main_res_o)
    assert res == (
        0), f"a = {a}, b = {b}, res = {res}"
    assert dut.main_sum_flags == (
        Z_FLAG), f"dut.main_sum_flags = {dut.main_sum_flags }"
    assert dut.main_sum_neg_ovflw == 0
    assert dut.main_sum_pos_ovflw == 0
