use rustc_serialize::json;
use mysql::prelude::*;
use config::*;
use std::collections::HashMap;

pub fn get_items() -> std::string::String {

        #[derive(Debug, PartialEq, Eq, RustcEncodable)]
        struct ItemData {
                key: i64,
                name: Option<String>
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

        let all_item_data: Vec<ItemData> =
        conn.query_iter("SELECT * FROM items;")
    .map(|result| {
        result.map(|x| x.unwrap()).map(|mut row| {

        ItemData {
            key: row.take("key").unwrap(),
            name: row.take("name").unwrap()
        }
        }).collect()}).unwrap();

        return json::encode(&all_item_data).unwrap();

}
