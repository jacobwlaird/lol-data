use rustc_serialize::json;
use mysql::prelude::*;
use config::*;
use std::collections::HashMap;

pub fn get_league_users() -> std::string::String {

        #[derive(Debug, PartialEq, Eq, RustcEncodable)]
        struct LeagueUsers {
                id: i64,
                summoner_name: Option<String>,
                riot_id: Option<String>
        }

        let mut settings = Config::default();
        settings.merge(File::with_name("config")).unwrap();
        let conf = settings.try_into::<HashMap<String, String>>().unwrap();

        //Build our connection string
        let mut url =  String::from("mysql://");
        url.push_str(conf.get("db_user").unwrap());
        url.push(':');
        url.push_str(conf.get("db_password").unwrap());
        url.push('@');
        url.push_str(&conf.get("db_id").unwrap());
        url.push(':');
        url.push_str("3306");
        url.push('/');
        url.push_str(&conf.get("db_name").unwrap());

        let pool = mysql::Pool::new(url).unwrap();
        let mut conn = pool.get_conn().unwrap();

        let all_league_users: Vec<LeagueUsers> =
        conn.query_iter("SELECT * FROM league_users;")
    .map(|result| {
        result.map(|x| x.unwrap()).map(|mut row| {

        LeagueUsers {
            id: row.take("id").unwrap(),
            summoner_name: row.take("summoner_name").unwrap(),
            riot_id: row.take("riot_id").unwrap()
        }
        }).collect()}).unwrap();

        return json::encode(&all_league_users).unwrap();

}
