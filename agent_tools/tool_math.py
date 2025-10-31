from fastmcp import FastMCP
import os
from dotenv import load_dotenv
load_dotenv()

mcp = FastMCP("Math")

@mcp.tool()
def add(a: float, b: float) -> float:
    """
    将两个数字相加（支持整数和浮点数）。

    Args:
        a (float): 第一个数字。
        b (float): 第二个数字。

    Returns:
        float: 两个数字的和。
    """
    return float(a) + float(b)

@mcp.tool()
def multiply(a: float, b: float) -> float:
    """
    将两个数字相乘（支持整数和浮点数）。

    Args:
        a (float): 第一个数字。
        b (float): 第二个数字。

    Returns:
        float: 两个数字的积。
    """
    return float(a) * float(b)

if __name__ == "__main__":
    port = int(os.getenv("MATH_HTTP_PORT", "8000"))
    mcp.run(transport="streamable-http", port=port)
