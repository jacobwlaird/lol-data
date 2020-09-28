import React from "react"
import { Input } from "reactstrap"

//The filter component for our DataTable Component
export const Filter = ({ column }) => {
    return (
	<div style={{ marginTop: 5 }}>
	    {column.canFilter && column.render("Filter")}
	</div>
    )
}

export const DefaultColumnFilter = ({
    column: {
	filterValue,
	setFilter,
	preFilteredRows: { length },
    },
    }) => {
        return (
	    <Input
	        value={filterValue || ""}
	        onChange={e => {
		    setFilter(e.target.value || undefined)
		}}
	        placeholder={'search'}
	    />
	)
}
