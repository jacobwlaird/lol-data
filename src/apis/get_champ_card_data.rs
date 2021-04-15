use std::io::Write;
use std::process::{Command, Stdio};
use actix_web::{HttpRequest};
use serde::{Deserialize};

pub fn get_champ_card_data(req: HttpRequest) -> std::string::String {
    //Figure out how to parse a request like in the other thing.
    #[derive(Deserialize)]
    struct ChampQuery{
        name:Option<String>,
        role:Option<String>,
        maxgames:Option<String>,
        incnone:Option<String>
    }

    let params: ChampQuery = serde_qs::from_str(req.query_string()).unwrap();
    let mut role = String::from("");
    let mut maxgames = String::from("");
    let mut incNone = String::from("");

    //I might have to do a giant ugly if statement for handling params that don't have values? 
    //Also how do we handle dates and defaults and stuff?
    
    //This one handles empty role?
    //if param.role is "", then do this one. otherwise...
    //This is close I think, but I gotta go.
    //For now we can count on sending role=All?
    //acutally this is just paniking right now and we'll have to deal with it later probably.
    match params.role {
        Some(p) => role = p,
        None => role = String::from("All")
    }

    match params.maxgames {
        Some(p) => maxgames = p,
        None => maxgames = String::from("50")
    }

    match params.incnone {
        Some(p) => incNone = p,
        None => incNone = String::from("false")
    }

    let output = Command::new("venv/bin/python").arg("./resources/python/get_champ_card_data.py").arg(params.name.unwrap()).arg(role).arg(maxgames).arg(incNone).output().unwrap();

    //This ones for having a role
    //let output = Command::new("venv/bin/python").arg("./resources/python/get_champ_card_data.py").arg(params.name.unwrap()).arg(params.role.unwrap()).output().unwrap();

    return std::string::String::from_utf8(output.stdout).unwrap();
}
