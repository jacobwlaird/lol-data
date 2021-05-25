use rustc_serialize::json;
use mysql::prelude::*;
use config::*;
use std::collections::HashMap;

pub fn get_champions() -> std::string::String {

        #[derive(Debug, PartialEq, Eq, RustcEncodable)]
        struct ChampData {
                key: i64,
                id: Option<String>,
                name: Option<String>,
                title: Option<String>,
                blurb: Option<String>
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

        let all_champ_data: Vec<ChampData> =
        conn.query_iter("SELECT * FROM champions;")
    .map(|result| {
        result.map(|x| x.unwrap()).map(|mut row| {

        ChampData{
            key: row.take("key").unwrap(),
            id: row.take("id").unwrap(),
            name: row.take("name").unwrap(),
            title: row.take("title").unwrap(),
            blurb: row.take("blurb").unwrap()
        }
        }).collect()}).unwrap();

        return json::encode(&all_champ_data).unwrap();

}
