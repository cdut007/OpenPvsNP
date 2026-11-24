# Mathematical Proof and Verification Standards

## Target statement
A direct route to P = NP is a deterministic algorithm deciding 3-SAT in polynomial time. Let n be the bit length of a specified encoding of a valid 3-CNF formula. A successful result must provide one fixed deterministic algorithm A and constants c > 0 and k such that, for every valid input F:
- A(F) halts;
- A(F) returns SAT exactly when F is satisfiable;
- A(F) returns UNSAT exactly when F is unsatisfiable; and
- the running time is at most c(n+1)^k in the specified computational model.

Because 3-SAT is NP-complete under standard polynomial-time reductions, such a result implies P = NP.

## Required components
1. Exact syntax and bit encoding of formulas and assignments.
2. Exact deterministic computational model (for example, a multitape Turing machine) and cost model.
3. Full algorithm, including preprocessing and all subroutines.
4. Proof of termination and correctness for all valid inputs.
5. Uniform worst-case time bound, with fixed constants and exponent.
6. Analysis of memory, integer bit lengths, data structures, recursion, branching, and hidden subroutines.
7. Explicit dependencies and assumptions, including imported theorems.
8. Independent review and reproducibility package.

## Common invalid shortcuts
- Fast performance on benchmarks or random instances.
- Average-case or high-probability bounds when a worst-case result is claimed.
- Polynomial behavior for each fixed parameter while the parameter is allowed to grow with input size.
- An unbounded or exponentially large branching factor or recursion tree.
- Treating unit-cost arithmetic on unbounded integers as constant time without justification.
- Hiding exponential work in preprocessing, lookup tables, or an oracle.
- Proving only one restricted family of formulas.
- Confusing a finite search with a uniform asymptotic theorem.

## Lean formalization
Lean can verify a formal derivation relative to its kernel and declared axioms. Every submission must disclose Lean and Mathlib versions, imported modules, and axiom dependencies. No `sorry`, custom axioms asserting the target, or unsound mechanisms are acceptable in a claimed proof. A formalization must encode the standard complexity-theoretic statement, not a weakened substitute.

## Status labels
Formal compilation, metadata validation, and experiments are evidence about their own scope only. They do not by themselves establish the target theorem.