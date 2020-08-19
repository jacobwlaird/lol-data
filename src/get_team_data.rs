use rustc_serialize::json;
use std::time::Instant;
use mysql::*;
use mysql::prelude::*;

pub fn get_team_data() -> std::string::String {
        let before = Instant::now();

        #[derive(Debug, PartialEq, Eq, RustcEncodable)]
        struct team_data {
                match_id: i64,
                game_version: Option<String>,
                win: Option<String>,
                participants: Option<String>,
              // // first_blood: u8,
              //  first_baron: u8,
              //  first_tower: u8,
              //  first_dragon: u8,
              //  first_inhib: u8,
              //  first_rift_herald: u8,
                first_blood: Option<String>,
                first_baron: Option<String>,
                first_tower: Option<String>,
                first_dragon: Option<String>,
                first_inhib: Option<String>,
               // first_rift_herald: u8,
               // dragon_kills: u8,
               // rift_herald_kills: u8,
               // inhib_kills: u8,
                first_rift_herald: Option<String>,
                dragon_kills: Option<String>,
                rift_herald_kills: Option<String>,
                inhib_kills: Option<String>,
                bans: Option<String>,
                enemy_bans: Option<String>,
                allies: Option<String>,
                enemies: Option<String>,
                start_time: Option<String>,
                duration: Option<String>
        }

        let url = "mysql://user:pass@ip:port/db"; // Don't hack me bro

        let pool = mysql::Pool::new(url).unwrap();
        let mut conn = pool.get_conn().unwrap();

        let mut all_team_data: Vec<team_data> = Vec::new();

        all_team_data =
        //conn.query_iter("SELECT * FROM team_data ORDER BY match_id DESC LIMIT 1")
        conn.query_iter("SELECT * FROM team_data ORDER BY match_id DESC;")
    .map(|result| {
        result.map(|x| x.unwrap()).map(|mut row| {

        team_data {
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
            dragon_kills: row.take("dragon_kills").unwrap(),
            rift_herald_kills: row.take("rift_herald_kills").unwrap(),
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


        println!("Elapsed time: {:.2?}", before.elapsed());

}
