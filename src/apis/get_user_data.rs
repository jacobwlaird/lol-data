use rustc_serialize::json;
use actix_web::{HttpRequest};
use mysql::prelude::*;
use config::*;
use std::collections::HashMap;
use serde::{Deserialize};

pub fn get_user_data(req: HttpRequest) -> std::string::String {

        #[derive(Deserialize)]
        struct UserQuery{
            name:Option<String>
        }

        let params: UserQuery = serde_qs::from_str(req.query_string()).unwrap();

        if params.name.is_none() {
            return "try adding ?name=dumat to the end of the url".to_string();

        }

        #[derive(Debug, PartialEq, Eq, RustcEncodable)]
        struct UserData {
                id: i64,
                match_id: i64,
                role: Option<String>,
                champion: Option<String>,
                champion_name: Option<String>,
                enemy_champion: Option<String>,
                enemy_champion_name: Option<String>,
                first_blood: Option<String>,
                first_blood_assist: Option<String>,
                kills: Option<String>,
                deaths: Option<String>,
                assists: Option<String>,
                damage_to_champs: Option<String>,
                damage_to_turrets: Option<String>,
                gold_per_minute: Option<String>,
                creeps_per_minute: Option<String>,
                xp_per_minute: Option<String>,
                wards_placed: Option<String>,
                vision_wards_bought: Option<String>,
                wards_killed: Option<String>,
                items: Option<String>,
                perks: Option<String>
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

        let user_match_data: Vec<UserData> =
        conn.query_iter(format!("SELECT * FROM match_data WHERE player = {:?} ORDER BY match_id DESC;", params.name.unwrap()))
    .map(|result| {
        result.map(|x| x.unwrap()).map(|mut row| {

        UserData {
            id: row.take("id").unwrap(),
            match_id: row.take("match_id").unwrap(),
            role: row.take("role").unwrap(),
            champion: row.take("champion").unwrap(),
            champion_name: row.take("champion_name").unwrap(),
            enemy_champion: row.take("enemy_champion").unwrap(),
            enemy_champion_name: row.take("enemy_champion_name").unwrap(),
            first_blood: row.take("first_blood").unwrap(),
            first_blood_assist: row.take("first_blood_assist").unwrap(),
            kills: row.take("kills").unwrap(),
            deaths: row.take("deaths").unwrap(),
            assists: row.take("assists").unwrap(),
            damage_to_champs: row.take("damage_to_champs").unwrap(),
            damage_to_turrets: row.take("damage_to_turrets").unwrap(),
            gold_per_minute: row.take("gold_per_minute").unwrap(),
            creeps_per_minute: row.take("creeps_per_minute").unwrap(),
            xp_per_minute: row.take("xp_per_minute").unwrap(),
            wards_placed: row.take("wards_placed").unwrap(),
            vision_wards_bought: row.take("vision_wards_bought").unwrap(),
            wards_killed: row.take("wards_killed").unwrap(),
            items: row.take("items").unwrap(),
            perks: row.take("perks").unwrap()
        }
        }).collect()}).unwrap();

        return json::encode(&user_match_data).unwrap();

}
