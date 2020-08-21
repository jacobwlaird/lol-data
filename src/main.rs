extern crate actix_files;
use actix_web::{middleware, web, App, HttpRequest, HttpServer};
use actix_files::Files;

#[path = "apis/get_team_data.rs"] mod get_team_data;
use get_team_data::get_team_data;

#[path = "apis/get_user_data.rs"] mod get_user_data;
use get_user_data::get_user_data;

async fn team_data() -> std::string::String {
    get_team_data()
}

async fn user_data(req: HttpRequest) -> std::string::String {
    get_user_data(req)
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
            .service(Files::new("/", "./build").index_file("index.html"))
    })
    .bind("127.0.0.1:5000")?
    .run()
    .await
}
