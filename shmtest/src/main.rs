use libafl::bolts::shmem::{ShMemProvider,StdShMemProvider,ShMem};
use std::env;
use std::process;

fn main() {
    const input_len: usize = 1024;
    let mut provider = StdShMemProvider::new().unwrap();
    let mut shmem = provider.new_shmem(input_len).unwrap();
    let env_var = "WSF_input";
    shmem.write_to_env(env_var);
    println!("{} in env: {}",env_var,env::var(env_var).unwrap());
    //Now write some data, gotta convert to u8 slice
    let input = unsafe { shmem.as_object_mut::<[u8; input_len]>() };
    input[0] = 0xa;
    input[1] = 0xb;
    input[2] = 0xc;
    input[3] = 0xd;
    loop {}
}
