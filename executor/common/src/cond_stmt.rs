use super::{cond_stmt_base::CondStmtBase, tag::TagSeg,cond_state::CondState};
use std::hash::{Hash, Hasher};
use serde_derive::{Deserialize, Serialize};

#[derive(Debug, Default, Clone, Serialize, Deserialize)]
pub struct CondStmt {
    pub base: CondStmtBase,
    pub offsets: Vec<TagSeg>,
    pub offsets_opt: Vec<TagSeg>,
    pub variables: Vec<u8>,

    pub speed: u32,
    pub is_desirable: bool, // non-convex
    pub is_consistent: bool,
    pub fuzz_times: usize,
    pub state: CondState,
    pub num_minimal_optima: usize,
    pub linear: bool,
}

impl PartialEq for CondStmt {
    fn eq(&self, other: &CondStmt) -> bool {
        self.base == other.base
    }
}

impl Eq for CondStmt {}

impl Hash for CondStmt {
    fn hash<H: Hasher>(&self, state: &mut H) {
        self.base.cmpid.hash(state);
        self.base.context.hash(state);
        self.base.order.hash(state);
    }
}

impl CondStmt {
    pub fn new() -> Self {
        let cond_base = Default::default();
        Self {
            base: cond_base,
            offsets: vec![],
            offsets_opt: vec![],
            variables: vec![],
            speed: 0,
            is_consistent: true,
            is_desirable: true,
            fuzz_times: 0,
            state: CondState::default(),
            num_minimal_optima: 0,
            linear: false,
        }
    }

    pub fn from(cond_base: CondStmtBase) -> Self {
        let mut cond = Self::new();
        cond.base = cond_base;
        cond
    }
}
