"""Package MCM — Matrix Chain Multiplication (Quy hoạch động Bottom-Up CLRS).

Public API tập trung tại đây để import gọn:

    from mcm import matrix_chain_order, print_optimal_parens, MCMSolver, DisplayMode, format_trace
"""

from mcm.solver import matrix_chain_order, print_optimal_parens, MCMSolver
from mcm.validator import validate_dimension_array
from mcm.formatter import DisplayMode, format_table, format_trace

__all__ = [
    "matrix_chain_order",
    "print_optimal_parens",
    "MCMSolver",
    "validate_dimension_array",
    "DisplayMode",
    "format_table",
    "format_trace",
]
