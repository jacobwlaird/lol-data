use rustc_serialize::json;
use mysql::prelude::*;
use config::*;
use std::collections::HashMap;

pub fn get_script_status() -> std::string::String {

        #[derive(Debug, PartialEq, Eq, RustcEncodable)]
        struct ScriptStatus {
                id: i64,
                source: Option<String>,
                status: Option<String>,
                matches_added: Option<String>,
                start_time: Option<String>,
                end_time: Option<String>,
                message: Option<String>
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

        let script_status: Vec<ScriptStatus> =
        conn.query_iter("SELECT * FROM script_runs ORDER BY id DESC LIMIT 1;")
    .map(|result| {
        result.map(|x| x.unwrap()).map(|mut row| {

        ScriptStatus {
            id: row.take("id").unwrap(),
            source: row.take("source").unwrap(),
            status: row.take("status").unwrap(),
            matches_added: row.take("matches_added").unwrap(),
            start_time: row.take("start_time").unwrap(),
            end_time: row.take("end_time").unwrap(),
            message: row.take("message").unwrap(),
        }
        }).collect()}).unwrap();

        return json::encode(&script_status).unwrap()
}
