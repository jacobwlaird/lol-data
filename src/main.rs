extern crate actix_files;
use actix_web::{middleware, web, App, HttpRequest, HttpServer, Result};
use actix_web::http::{StatusCode};
use actix_files::Files;
use actix_files::NamedFile;

#[path = "apis/get_team_data.rs"] mod get_team_data;
use get_team_data::get_team_data;

#[path = "apis/get_user_data.rs"] mod get_user_data;
use get_user_data::get_user_data;

#[path = "apis/update_data.rs"] mod update_data;
use update_data::update_data;

#[path = "apis/get_script_status.rs"] mod get_script_status;
use get_script_status::get_script_status;

#[path = "apis/get_league_users.rs"] mod get_league_users;
use get_league_users::get_league_users;

#[path = "apis/get_json_data.rs"] mod get_json_data;
use get_json_data::get_json_data;

#[path = "apis/get_items.rs"] mod get_items;
use get_items::get_items;

#[path = "apis/get_script_runs.rs"] mod get_script_runs;
use get_script_runs::get_script_runs;

#[path = "apis/get_champions.rs"] mod get_champions;
use get_champions::get_champions;

#[path = "apis/get_champ_card_data.rs"] mod get_champ_card_data;
use get_champ_card_data::get_champ_card_data;

async fn team_data() -> std::string::String {
    get_team_data()
}

async fn user_data(req: HttpRequest) -> std::string::String {
    get_user_data(req)
}

async fn update() -> std::string::String {
    update_data()
}

async fn script_status() -> std::string::String {
    get_script_status()
}


async fn league_users() -> std::string::String {
    get_league_users()
}

async fn json_data() -> std::string::String {
    get_json_data()
}

async fn items() -> std::string::String {
    get_items()
}

async fn script_runs() -> std::string::String {
    get_script_runs()
}

async fn champions() -> std::string::String {
    get_champions()
}

async fn champ_card_data(req: HttpRequest) -> std::string::String {
    get_champ_card_data(req)
}

async fn route_to_index() -> Result<NamedFile> {

    Ok(NamedFile::open("build/index.html")?.set_status_code(StatusCode::NOT_FOUND))
}

#[actix_rt::main]
async fn main() -> std::io::Result<()> {
    std::env::set_var("RUST_LOG", "actix_web=info");
    env_logger::init();

    HttpServer::new(|| {
        App::new()
            // enable logger
            .wrap(middleware::Logger::default())
            .service(web::resource("/api/get_team_data").to(team_data))
            .service(web::resource("/api/get_user_data").to(user_data))
            .service(web::resource("/api/update_data").to(update))
            .service(web::resource("/api/get_script_status").to(script_status))
            .service(web::resource("/api/get_league_users").to(league_users))
            .service(web::resource("/api/get_json_data").to(json_data))
            .service(web::resource("/api/get_items").to(items))
            .service(web::resource("/api/get_script_runs").to(script_runs))
            .service(web::resource("/api/get_champions").to(champions))
            .service(web::resource("/api/get_champ_card_data").to(champ_card_data))
            .service(Files::new("/", "./build").index_file("index.html"))
            .default_service(web::to(route_to_index))
    })
    .bind("0.0.0.0:5000")?
    .run()
    .await
}
