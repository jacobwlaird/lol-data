extern crate actix_files;
use actix_web::{middleware, web, App, HttpServer};
use actix_files::Files;
mod get_team_data;
use get_team_data::get_team_data;

async fn team_data() -> std::string::String {
    get_team_data()
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
            .service(Files::new("/", "./build").index_file("index.html"))
    })
    .bind("127.0.0.1:5000")?
    .run()
    .await
}
