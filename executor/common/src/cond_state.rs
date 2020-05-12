use serde_derive::{Deserialize, Serialize};

#[derive(Debug, Clone, PartialEq, Eq, Serialize, Deserialize)]
pub enum CondState {
    Offset,
    OffsetOpt,
    OffsetAll,
    OffsetAllEnd,

    OneByte,
    Unsolvable,
    Deterministic,
    Timeout,
}

impl Default for CondState {
    fn default() -> Self {
        CondState::Offset
    }
}

