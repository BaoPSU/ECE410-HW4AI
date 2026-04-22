import cocotb
from cocotb.clock import Clock
from cocotb.triggers import RisingEdge, Timer


async def reset(dut):
    dut.rst.value = 1
    dut.a.value = 0
    dut.b.value = 0
    await RisingEdge(dut.clk)
    await Timer(1, unit="ns")
    dut.rst.value = 0


@cocotb.test()
async def test_mac_basic(dut):
    """Basic accumulation: a=3,b=4 x3 cycles, rst, a=-5,b=2 x2 cycles."""
    cocotb.start_soon(Clock(dut.clk, 10, unit="ns").start())
    await reset(dut)

    dut.a.value = 3
    dut.b.value = 4
    for expected in [12, 24, 36]:
        await RisingEdge(dut.clk)
        await Timer(1, unit="ns")
        got = dut.out.value.to_signed()
        assert got == expected, f"Expected {expected}, got {got}"
        dut._log.info(f"out = {got} (expected {expected}) PASS")

    dut.rst.value = 1
    await RisingEdge(dut.clk)
    await Timer(1, unit="ns")
    got = dut.out.value.to_signed()
    assert got == 0, f"After rst: expected 0, got {got}"
    dut._log.info(f"After rst: out = {got} PASS")

    dut.rst.value = 0
    dut.a.value = 0xFB  # -5 in two's complement INT8
    dut.b.value = 2
    for expected in [-10, -20]:
        await RisingEdge(dut.clk)
        await Timer(1, unit="ns")
        got = dut.out.value.to_signed()
        assert got == expected, f"Expected {expected}, got {got}"
        dut._log.info(f"out = {got} (expected {expected}) PASS")

    dut._log.info("test_mac_basic PASSED")


@cocotb.test()
async def test_mac_overflow(dut):
    """Overflow: accumulate a=127,b=127 (~133k cycles) until 32-bit signed wraps."""
    cocotb.start_soon(Clock(dut.clk, 10, unit="ns").start())
    await reset(dut)

    # product = 127*127 = 16129 per cycle; overflow at ~133,145 cycles
    dut.a.value = 127
    dut.b.value = 127

    prev = 0
    wrapped = False
    for i in range(150_000):
        await RisingEdge(dut.clk)
        await Timer(1, unit="ns")
        current = dut.out.value.to_signed()
        if current < prev:
            wrapped = True
            dut._log.info(
                f"Overflow wrap at cycle {i + 1}: {prev} -> {current}"
            )
            dut._log.info(
                "Behavior: wraps (two's complement). "
                "No saturation — design does not clamp at 2^31-1."
            )
            break
        prev = current

    assert wrapped, "No overflow in 150,000 cycles"
    dut._log.info("test_mac_overflow PASSED")
