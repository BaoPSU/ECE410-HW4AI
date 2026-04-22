import cocotb
from cocotb.clock import Clock
from cocotb.triggers import RisingEdge, Timer


K = 16
D = 3
DATA_W = 8


async def reset(dut):
    dut.rst_n.value = 0
    dut.start.value = 0
    for d in range(D):
        dut.pixel[d].value = 0
    for i in range(K * D):
        dut.centroids[i].value = 0
    await RisingEdge(dut.clk)
    await Timer(1, unit="ns")
    dut.rst_n.value = 1


def set_centroids(dut, centroid_list):
    """centroid_list: list of K lists of D channel values."""
    for k in range(K):
        for d in range(D):
            dut.centroids[k * D + d].value = centroid_list[k][d]


@cocotb.test()
async def test_kmeans_nearest(dut):
    """Black pixel (0,0,0) nearest to centroid 0 at (0,0,0); others at 128 or 255."""
    cocotb.start_soon(Clock(dut.clk, 10, unit="ns").start())
    await reset(dut)

    # Centroid 0 at (0,0,0); centroid 1 at (128,128,128); rest at (255,255,255)
    centroids = [[0, 0, 0]] + [[128, 128, 128]] + [[255, 255, 255]] * (K - 2)
    set_centroids(dut, centroids)

    for d in range(D):
        dut.pixel[d].value = 0  # black pixel

    dut.start.value = 1
    await RisingEdge(dut.clk)
    await Timer(1, unit="ns")
    dut.start.value = 0

    assert dut.done.value == 1, "done not asserted after start"
    got_label = int(dut.label.value)
    got_dist  = int(dut.min_dist.value)
    assert got_label == 0, f"Expected label=0 (centroid at origin), got {got_label}"
    assert got_dist  == 0, f"Expected min_dist=0, got {got_dist}"
    dut._log.info(f"label={got_label} min_dist={got_dist}  PASS")

    # Verify done de-asserts next cycle (no start)
    await RisingEdge(dut.clk)
    await Timer(1, unit="ns")
    assert dut.done.value == 0, "done should de-assert when start=0"
    dut._log.info("done de-asserted correctly  PASS")
    dut._log.info("test_kmeans_nearest PASSED")


@cocotb.test()
async def test_kmeans_midpoint(dut):
    """Gray pixel (128,128,128) nearest to centroid 1 at (128,128,128)."""
    cocotb.start_soon(Clock(dut.clk, 10, unit="ns").start())
    await reset(dut)

    centroids = [[0, 0, 0]] + [[128, 128, 128]] + [[255, 255, 255]] * (K - 2)
    set_centroids(dut, centroids)

    for d in range(D):
        dut.pixel[d].value = 128

    dut.start.value = 1
    await RisingEdge(dut.clk)
    await Timer(1, unit="ns")
    dut.start.value = 0

    assert dut.done.value == 1
    got_label = int(dut.label.value)
    got_dist  = int(dut.min_dist.value)
    assert got_label == 1, f"Expected label=1 (gray centroid), got {got_label}"
    assert got_dist  == 0, f"Expected min_dist=0 for exact match, got {got_dist}"
    dut._log.info(f"label={got_label} min_dist={got_dist}  PASS")
    dut._log.info("test_kmeans_midpoint PASSED")
