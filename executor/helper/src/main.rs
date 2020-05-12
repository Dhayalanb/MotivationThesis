extern crate angora_common;
use angora_common::{defs, cond_stmt::CondStmt, tag::TagSeg, log_data::LogData};
use std::{env, path::Path, path::PathBuf, fs, io, collections::HashMap};
use bincode::{deserialize_from};
use byteorder::{LittleEndian, WriteBytesExt};
use serde_json;

fn main() {
    let args: Vec<String> = env::args().collect();
    if args.len() <= 1 {
        println!("Wrong command!");
        return;
    }

    let path = PathBuf::from(&args[1]);

    // let t = load_track_data(path.as_path(), 0, 0, 0, 0);
    let t = match read_and_parse(path.as_path(), false) {
        Result::Ok(val) => val,
        Result::Err(err) => panic!("parse track file error!! {:?}", err),
    };
    let json = get_json(&t);
    println!("{}", json);
}

pub fn get_json(t: &Vec<CondStmt>) -> String {
    match serde_json::to_string(&t) {
        Result::Ok(val) => return val,
        Result::Err(err) => panic!("Failed to serialize to json!! {:?}", err),
    };
}

pub fn read_and_parse(
    out_f: &Path,
    enable_exploitation: bool,
) -> io::Result<Vec<CondStmt>> {
    let log_data = {
        get_log_data(out_f)?
    };

    let mut cond_list: Vec<CondStmt> = Vec::new();
    // assign taint labels and magic_bytes to cond list
    for (i, cond_base) in log_data.cond_list.iter().enumerate() {
        if !enable_exploitation {
            if cond_base.is_exploitable() {
                continue;
            }
        }
        let mut cond = CondStmt::from(*cond_base);
        if cond_base.op != defs::COND_LEN_OP && (cond_base.lb1 > 0 || cond_base.lb2 > 0) {
            if cond_base.size == 0 {
                println!("cond: {:?}", cond_base);
            }
            get_offsets_and_variables(&log_data.tags, &mut cond, &log_data.magic_bytes.get(&i));
        }

        cond_list.push(cond);
    }
    Ok(cond_list)
}

fn get_offsets_and_variables(
    m: &HashMap<u32, Vec<TagSeg>>,
    cond: &mut CondStmt,
    magic_bytes: &Option<&(Vec<u8>, Vec<u8>)>,
) {
    let empty_offsets: Vec<TagSeg> = vec![];
    let offsets1 = m.get(&cond.base.lb1).unwrap_or(&empty_offsets);
    let offsets2 = m.get(&cond.base.lb2).unwrap_or(&empty_offsets);
    if offsets2.len() == 0 || (offsets1.len() > 0 && offsets1.len() <= offsets2.len()) {
        cond.offsets = offsets1.clone();
        if cond.base.lb2 > 0 && cond.base.lb1 != cond.base.lb2 {
            cond.offsets_opt = offsets2.clone();
        }
        cond.variables = if let Some(args) = magic_bytes {
            [&args.1[..], &args.0[..]].concat()
        } else {
            // if it is integer comparison, we use the bytes of constant as magic bytes.
            write_as_ule(cond.base.arg2, cond.base.size as usize)
        };
    } else {
        cond.offsets = offsets2.clone();
        if cond.base.lb1 > 0 && cond.base.lb1 != cond.base.lb2 {
            cond.offsets_opt = offsets1.clone();
        }
        cond.variables = if let Some(args) = magic_bytes {
            [&args.0[..], &args.1[..]].concat()
        } else {
            write_as_ule(cond.base.arg1, cond.base.size as usize)
        };
    }
}

pub fn get_log_data(path: &Path) -> io::Result<LogData> {
    let f = fs::File::open(path)?;
    if f.metadata().unwrap().len() == 0 {
        return Err(io::Error::new(io::ErrorKind::Other, "Could not find any interesting constraint!, Please make sure taint tracking works or running program correctly."));
    }
    let mut reader = io::BufReader::new(f);
    match deserialize_from::<&mut io::BufReader<fs::File>, LogData>(&mut reader) {
        Ok(v) => Ok(v),
        Err(_) => Err(io::Error::new(io::ErrorKind::Other, "bincode parse error!")),
    }
}

pub fn write_as_ule(val: u64, size: usize) -> Vec<u8> {
    let mut wtr = vec![];
    match size {
        1 => {
            wtr.write_u8(val as u8).unwrap();
        },
        2 => {
            wtr.write_u16::<LittleEndian>(val as u16).unwrap();
        },
        4 => {
            wtr.write_u32::<LittleEndian>(val as u32).unwrap();
        },
        8 => {
            wtr.write_u64::<LittleEndian>(val as u64).unwrap();
        },
        _ => {
            println!("wrong size: {:?}", size);
            // panic!("strange arg size: {}", size);
        },
    }

    wtr
}