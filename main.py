from solve import solve_model, Solver


if __name__ == "__main__":
    solve_model("caso2", {"solver": Solver.GUROBI_CMD, "gapRel": 0.1, "maxNodes": 5000})
