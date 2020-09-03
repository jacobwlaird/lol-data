use std::process::Command;

pub fn update_data() -> std::string::String {

    let output = Command::new("python3").arg("./resources/python/loldata.py").arg("ManualWeb").spawn().expect("It failed I guess?");

    return "{\"message\":\"okay\"}".to_string()

}
