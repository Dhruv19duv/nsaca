//! Compiler-inspired optimization passes.
//!
//! Provides peephole optimizations, constant folding, dead code elimination,
//! and strength reduction for generated code.

/// Represents an instruction in the NSACA intermediate representation.
#[derive(Debug, Clone, PartialEq)]
pub enum Instruction {
    Load(i64),
    Add,
    Mul,
    Store(usize),
    Branch(usize),
    ConditionalBranch(usize),
    Phi(Vec<i64>),
    NoOp,
}

/// A simple optimizer that applies peephole and constant folding passes.
pub struct Optimizer {
    instructions: Vec<Instruction>,
}

impl Optimizer {
    pub fn new(instructions: Vec<Instruction>) -> Self {
        Optimizer { instructions }
    }

    /// Apply all optimization passes and return optimized instructions.
    pub fn optimize(&mut self) -> Vec<Instruction> {
        self.constant_folding();
        self.dead_code_elimination();
        self.peephole();
        self.instructions.clone()
    }

    /// Constant folding: evaluate constant expressions at compile time.
    fn constant_folding(&mut self) {
        let mut i = 0;
        while i + 1 < self.instructions.len() {
            if let (Instruction::Load(a), Instruction::Load(b)) =
                (&self.instructions[i], &self.instructions[i + 1])
            {
                if i + 2 < self.instructions.len() {
                    match &self.instructions[i + 2] {
                        Instruction::Add => {
                            self.instructions[i] = Instruction::Load(a + b);
                            self.instructions.remove(i + 2);
                            self.instructions.remove(i + 1);
                            continue;
                        }
                        Instruction::Mul => {
                            self.instructions[i] = Instruction::Load(a * b);
                            self.instructions.remove(i + 2);
                            self.instructions.remove(i + 1);
                            continue;
                        }
                        _ => {}
                    }
                }
            }
            i += 1;
        }
    }

    /// Dead code elimination: remove unreachable instructions after branches.
    fn dead_code_elimination(&mut self) {
        let mut keep = vec![true; self.instructions.len()];
        let mut unreachable = false;

        for (i, inst) in self.instructions.iter().enumerate() {
            if unreachable {
                keep[i] = false;
                continue;
            }
            if matches!(inst, Instruction::Branch(_) | Instruction::ConditionalBranch(_)) {
                unreachable = true;
            }
        }

        self.instructions = self
            .instructions
            .iter()
            .zip(keep)
            .filter(|(_, k)| *k)
            .map(|(inst, _)| inst.clone())
            .collect();
    }

    /// Peephole optimizations: strength reduction and pattern matching.
    fn peephole(&mut self) {
        let mut i = 0;
        while i < self.instructions.len() {
            // Strength reduction: x * 1 -> x
            if i + 1 < self.instructions.len() {
                if let Instruction::Load(1) = self.instructions[i + 1] {
                    if self.instructions[i] == Instruction::Mul {
                        self.instructions.remove(i + 1);
                        self.instructions[i] = Instruction::NoOp;
                        i += 1;
                        continue;
                    }
                }
                // x * 0 -> Load(0)
                if let Instruction::Load(0) = self.instructions[i + 1] {
                    if self.instructions[i] == Instruction::Mul {
                        self.instructions[i] = Instruction::Load(0);
                        self.instructions.remove(i + 1);
                        continue;
                    }
                }
                // x + 0 -> x
                if let Instruction::Load(0) = self.instructions[i + 1] {
                    if self.instructions[i] == Instruction::Add {
                        self.instructions.remove(i + 1);
                        self.instructions[i] = Instruction::NoOp;
                        i += 1;
                        continue;
                    }
                }
            }
            i += 1;
        }
    }
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn test_constant_folding() {
        let instructions = vec![
            Instruction::Load(3),
            Instruction::Load(4),
            Instruction::Add,
        ];
        let mut opt = Optimizer::new(instructions);
        let result = opt.optimize();
        assert_eq!(result[0], Instruction::Load(7));
    }

    #[test]
    fn test_peephole_mul_one() {
        let instructions = vec![
            Instruction::Load(5),
            Instruction::Load(1),
            Instruction::Mul,
        ];
        let mut opt = Optimizer::new(instructions);
        let result = opt.optimize();
        assert!(result.contains(&Instruction::NoOp));
    }
}
