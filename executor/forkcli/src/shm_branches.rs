// map branch counting shared memory.

//NEVER CALLED, USED TO KEEP TRACK OF NEW BRANCHES VIA SHARED MEMORY
use angora_common::config::BRANCHES_SIZE;
use angora_common::defs::BRANCHES_SHM_ENV_VAR;
use angora_common::shm;
use std::env;
use std::process;

pub type BranchBuf = [u8; BRANCHES_SIZE];
static mut __ANGORA_AREA_INITIAL: BranchBuf = [255; BRANCHES_SIZE];

#[no_mangle]
pub static mut __angora_area_ptr: *const u8 = unsafe{  &__ANGORA_AREA_INITIAL[0] as *const u8 };

pub fn map_branch_counting_shm() {
    let id_val = env::var(BRANCHES_SHM_ENV_VAR);
    match id_val {
        Ok(val) => {
            let shm_id = val.parse::<i32>().expect("Could not parse i32 value.");
            let mem = shm::SHM::<BranchBuf>::from_id(shm_id);
            if mem.is_fail() {
              eprintln!("fail to load shm");
              process::exit(1);
            }
            unsafe {
                __angora_area_ptr = mem.get_ptr() as *const u8;
            }
            return;
        }
        Err(_) => {}
    }

}
