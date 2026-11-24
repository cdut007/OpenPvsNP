import Std

/-!
A minimal syntactic foundation for 3-SAT. This file makes no claim about
complexity and contains no axiom asserting P = NP or P != NP.
Encoding length and machine complexity remain separate research tasks.
-/

namespace OpenPvsNP

structure Literal where
  variable : Nat
  positive : Bool
  deriving DecidableEq, Repr

structure Clause where
  first : Literal
  second : Literal
  third : Literal
  deriving DecidableEq, Repr

abbrev Formula := List Clause
abbrev Assignment := Nat → Bool

def evalLiteral (assignment : Assignment) (lit : Literal) : Bool :=
  if lit.positive then assignment lit.variable else !(assignment lit.variable)

def satisfiesClause (assignment : Assignment) (clause : Clause) : Bool :=
  evalLiteral assignment clause.first ||
    evalLiteral assignment clause.second ||
    evalLiteral assignment clause.third

def satisfies (assignment : Assignment) (formula : Formula) : Bool :=
  formula.all (satisfiesClause assignment)

def Satisfiable (formula : Formula) : Prop :=
  ∃ assignment : Assignment, satisfies assignment formula = true

def Unsatisfiable (formula : Formula) : Prop :=
  ∀ assignment : Assignment, satisfies assignment formula = false

end OpenPvsNP
