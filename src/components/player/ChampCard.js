//What was I even doing?
//all I know is there was a class called "champCardRoot" that
//I think champ card had a 'picture' and a stats component.
//champ card accepted className and data, but what is classname?

import React from 'react';
import { makeStyles } from '@material-ui/core/styles';
import Stats from  './Stats';
import "bootstrap/dist/css/bootstrap.min.css"
import './ChampCard.css';

const ChampCard = ({data}) => {
    return (
	    <div className="champCardRoot">

	    <p className="champ_name" style={{
			    backgroundColor: ((data.win_rate > .50)?`rgba(0,255,0,.2)`: `rgba(255,0,0,.2)`)}}>{data.champion} - {data.role}</p>
	    <Stats data={data} />
	    </div>
    );
}

export default ChampCard;
