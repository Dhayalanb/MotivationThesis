// corresponding to fuzzer/src/cond_stmt/shm_conds.rs

use angora_common::{cond_stmt_base::CondStmtBase, shm};
use std::{ops::DerefMut, sync::Mutex};
use super::{context};
use lazy_static::lazy_static;

#[no_mangle]
static mut __angora_cond_cmpid: u32 = 0;

#[inline(always)]
fn set_cmpid(cid: u32) {
    unsafe {
        __angora_cond_cmpid = cid;
    }
}

pub struct ShmConds {
    cond: shm::SHM<CondStmtBase>,
    rt_order: u32,
}

// shm contains pointer..
unsafe impl Send for ShmConds {}

// Drop in common/shm.rs:
// Though SHM<T> implement "drop" function, but it won't call (as we want) since ShmConds is in lazy_static!
impl ShmConds {
    pub fn get_shm() -> Self {
        println!("Creating new SHM");
        return Self {
            cond : shm::SHM::<CondStmtBase>::new(),
            rt_order : 0,
        }
    }

    pub fn get_condition(&mut self) -> CondStmtBase {
        return *self.cond;
    }

    pub fn update_cond_stmt_base(&mut self, cond_stmt_base: CondStmtBase) {
        self.cond.cmpid = cond_stmt_base.cmpid;
        self.cond.context = cond_stmt_base.context;
        self.cond.order = cond_stmt_base.order;
        self.cond.belong = cond_stmt_base.belong;
        self.cond.condition = cond_stmt_base.condition;
        self.cond.level = cond_stmt_base.level;
        self.cond.op = cond_stmt_base.op;
        self.cond.size = cond_stmt_base.size;
        self.cond.lb1 = cond_stmt_base.lb1;
        self.cond.lb2 = cond_stmt_base.lb2;
        self.cond.arg1 = cond_stmt_base.arg1;
        self.cond.arg2 = cond_stmt_base.arg2;
    }

    #[inline(always)]
    fn mark_reachable(&mut self, condition: u32) {
        self.cond.lb1 = condition;
    }

    pub fn check_match(&mut self, cmpid: u32, context: u32) -> bool {
        if self.cond.cmpid == cmpid && self.cond.context == context {
            self.rt_order += 1;
            if self.cond.order & 0xFFFF == self.rt_order {
                return true;
            }
        }
        false
    }

    pub fn update_cmp(&mut self, condition: u32, arg1: u64, arg2: u64) -> u32 {
        self.cond.arg1 = arg1;
        self.cond.arg2 = arg2;
        self.rt_order = 0x8000;
        self.mark_reachable(condition);
        set_cmpid(0);
        condition
    }

    pub fn update_switch(&mut self, condition: u64) -> u64 {
        self.cond.arg1 = condition;
        self.rt_order = 0x8000;
        self.mark_reachable((condition == self.cond.arg2) as u32);
        set_cmpid(0);
        condition
    }

    pub fn reset(&mut self) {
        self.rt_order = 0;
        set_cmpid(self.cond.cmpid);
    }
}

lazy_static! {
    pub static ref SHM_CONDS: Mutex<Option<ShmConds>> = Mutex::new(Some(ShmConds::get_shm()));
}

#[inline(always)]
pub fn reset_shm_conds() {
    println!("print works from child!2");
    let mut conds = SHM_CONDS.lock().expect("SHM mutex poisoned.");
    println!("print works from child!3");
    match conds.deref_mut() {
        &mut Some(ref mut c) => {
            println!("Resetting");
            c.reset();
        }
        _ => {println!("ERROR!!!");}
    }

    unsafe {
        context::reset_context();
    }
}
