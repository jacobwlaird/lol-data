import React, { Fragment} from 'react';
import { useTable, usePagination, useFilters, useSortBy } from 'react-table';
import { Table, Row, Col, Button, Input, CustomInput  } from 'reactstrap'
import { Filter, DefaultColumnFilter } from './Filter.js'

//Pagination

const MyTable = ({columns, data, getCellProps}) => {
    const {
			getTableProps,
			getTableBodyProps,
			headerGroups,
			page,
			prepareRow,
			canPreviousPage,
			canNextPage,
			pageOptions,
			pageCount,
			gotoPage,
			nextPage,
			previousPage,
			setPageSize,
			state: { pageIndex, pageSize}
		} = useTable(
		{
			columns,
			data,
			initialState: { pageIndex: 0, pageSize: 10},
			defaultColumn: {Filter: DefaultColumnFilter},
		},
		useFilters,
		useSortBy,
		usePagination
	);

	const onChangeInSelect = event => {
		  setPageSize(Number(event.target.value))
	}

	const onChangeInInput = event => {
		  const page = event.target.value ? Number(event.target.value) - 1 : 0
		  gotoPage(page)
	}

	const generateSortingIndicator = column => {
		  return column.isSorted ? (column.isSortedDesc ? " 🔽" : " 🔼") : ""
	}

    return (
		<Fragment> 
	<Table bordered hover {...getTableProps()}>
		<thead>
			{headerGroups.map(headerGroup => (
				<tr {...headerGroup.getHeaderGroupProps()}>
					{headerGroup.headers.map(column=> (
						<th style={{"width": column.width}} {...column.getHeaderProps()}>
						<div {...column.getSortByToggleProps()}>
						{column.render("Header")}
						{generateSortingIndicator(column)}
						</div>
						<Filter column={column}/>
						</th>
					))}
				</tr>
			))}
		</thead>

		<tbody {...getTableBodyProps()}>
			{page.map(row => {
				prepareRow(row)
				return (
					<tr {...row.getRowProps()}>
						{row.cells.map(cell => {
							return <td {...cell.getCellProps([getCellProps(cell)])}>
									{cell.render("Cell")}
								</td>
						})}
					</tr>
			)
			})}
		</tbody>
	</Table>
		<Row style={{ maxWidth: 1000, margin: "0 auto", textAlign: "center" }}>
		    <Col md={3}>
		      <Button
		        color="primary"
		        onClick={() => gotoPage(0)}
		        disabled={!canPreviousPage}
		      >
		        {"<<"}
		      </Button>
		      <Button
		        color="primary"
		        onClick={previousPage}
		        disabled={!canPreviousPage}
		      >
		        {"<"}
		      </Button>
		    </Col>
		    <Col md={2} style={{ marginTop: 7 }}>
		      Page{" "}
		      <strong>
		        {pageIndex + 1} of {pageOptions.length}
		      </strong>
		    </Col>
		    <Col md={2}>
		      <Input
		        type="number"
		        min={1}
		        style={{ width: 70 }}
		        max={pageOptions.length}
		        defaultValue={pageIndex + 1}
		        onChange={onChangeInInput}
		      />
		    </Col>
		    <Col md={2}>
		      <CustomInput id="custInput" type="select" value={pageSize} onChange={onChangeInSelect}>
		        >
		        {[10, 20, 30, 40, 50].map(pageSize => (
					          <option key={pageSize} value={pageSize}>
					            Show {pageSize}
					          </option>
					        ))}
		      </CustomInput>
		    </Col>
		    <Col md={3}>
		      <Button color="primary" onClick={nextPage} disabled={!canNextPage}>
		        {">"}
		      </Button>
		      <Button
		        color="primary"
		        onClick={() => gotoPage(pageCount - 1)}
		        disabled={!canNextPage}
		      >
		        {">>"}
		      </Button>
		    </Col>
		  </Row>
		</Fragment>

    )
}

export default MyTable
