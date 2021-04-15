//there's a StatsRoot class. That's all I know.
// I want to change the color of the win ratio to be green/red/yellow
// Might switch this to a two column thing where I put all the numbers right aligned.
import React from 'react';
import { makeStyles } from '@material-ui/core/styles';
import "bootstrap/dist/css/bootstrap.min.css";
import './Stats.css';

const Stats = ({data}) => {
    return (
	    <div className="statsRoot">
	    <p className="stat">Kda: {data.kda}</p>
	    <p className="stat">Games: {data.games}</p>
	    <p className="stat">Win Rate: {data.win_rate}</p>
	    <p className="stat">Gld per Min: {data.gpm}</p>
	    <p className="stat">CS per Min: {data.cspm}</p>
	    <p className="stat">Avg. Tower Dmg: {data.tower_damage}</p>
	    <p className="stat">Avg. Champ Dmg: {data.champion_damage}</p>
	    <p className="stat">Avg. Wards Placed: {data.wards_placed}</p>
	    <p className="stat">Avg. Pinks Get: {data.vision_wards_bought}</p>
	    <p className="stat">Avg. Wards Kill: {data.wards_killed}</p>
	    </div>
    );
}

export default Stats
