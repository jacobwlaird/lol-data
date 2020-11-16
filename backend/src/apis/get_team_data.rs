use rustc_serialize::json;
use mysql::prelude::*;
use config::*;
use std::collections::HashMap;

pub fn get_team_data() -> std::string::String {

        #[derive(Debug, PartialEq, Eq, RustcEncodable)]
        struct TeamData {
                match_id: i64,
                game_version: Option<String>,
                win: Option<String>,
                participants: Option<String>,
                first_blood: Option<String>,
                first_baron: Option<String>,
                first_tower: Option<String>,
                first_dragon: Option<String>,
                first_inhib: Option<String>,
                first_rift_herald: Option<String>,
                ally_dragon_kills: Option<String>,
                ally_rift_herald_kills: Option<String>,
                enemy_dragon_kills: Option<String>,
                enemy_rift_herald_kills: Option<String>,
                inhib_kills: Option<String>,
                bans: Option<String>,
                enemy_bans: Option<String>,
                allies: Option<String>,
                enemies: Option<String>,
                start_time: Option<String>,
                duration: Option<String>
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

        let all_team_data: Vec<TeamData> =
        conn.query_iter("SELECT * FROM team_data ORDER BY match_id DESC;")
    .map(|result| {
        result.map(|x| x.unwrap()).map(|mut row| {

        TeamData {
            match_id: row.take("match_id").unwrap(),
            game_version: row.take("game_version").unwrap(),
            win: row.take("win").unwrap(),
            participants: row.take("participants").unwrap(),
            first_blood: row.take("first_blood").unwrap(),
            first_baron: row.take("first_baron").unwrap(),
            first_tower: row.take("first_tower").unwrap(),
            first_dragon: row.take("first_dragon").unwrap(),
            first_inhib: row.take("first_inhib").unwrap(),
            first_rift_herald: row.take("first_rift_herald").unwrap(),
            ally_dragon_kills: row.take("ally_dragon_kills").unwrap(),
            ally_rift_herald_kills: row.take("ally_rift_herald_kills").unwrap(),
            enemy_dragon_kills: row.take("enemy_dragon_kills").unwrap(),
            enemy_rift_herald_kills: row.take("enemy_rift_herald_kills").unwrap(),
            inhib_kills: row.take("inhib_kills").unwrap(),
            bans: row.take("bans").unwrap(),
            enemy_bans: row.take("enemy_bans").unwrap(),
            allies: row.take("allies").unwrap(),
            enemies: row.take("enemies").unwrap(),
            start_time: row.take("start_time").unwrap(),
            duration: row.take("duration").unwrap()
        }
        }).collect()}).unwrap();

        return json::encode(&all_team_data).unwrap();

}
