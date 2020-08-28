use rustc_serialize::json;
use std::{thread, time};
use std::process::Command;

pub fn update_data() -> std::string::String {

    let output = Command::new("python").arg("./resources/python/loldata.py").output().expect("It failed I guess?");

    let my_dumb_string = &String::from_utf8(output.stdout).unwrap();

    //Make this better later, probably.
    return "{\"Hey\": \"It's done\"}".to_string();

}
