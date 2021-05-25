use rustc_serialize::json;
use mysql::prelude::*;
use config::*;
use std::collections::HashMap;

pub fn get_json_data() -> std::string::String {

        #[derive(Debug, PartialEq, Eq, RustcEncodable)]
        struct JsonData {
                match_id: i64,
                json_data: Option<String>
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

        let all_json_data: Vec<JsonData> =
        conn.query_iter("SELECT * FROM json_data;")
    .map(|result| {
        result.map(|x| x.unwrap()).map(|mut row| {

        JsonData {
            match_id: row.take("match_id").unwrap(),
            json_data: row.take("json_data").unwrap()
        }
        }).collect()}).unwrap();

        return json::encode(&all_json_data).unwrap();

}
