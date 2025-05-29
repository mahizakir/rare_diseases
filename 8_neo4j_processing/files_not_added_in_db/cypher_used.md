CALL {
    LOAD CSV WITH HEADERS FROM 'file:///final_nodes.csv' AS row
    WITH row
    CALL apoc.create.node([row.label], {
        id: toInteger(row.id),
        name: row.name,
        article_name: row.article_name,
        disease_name: row.disease_name
    }) YIELD node
    RETURN count(*) as created
} IN TRANSACTIONS OF 500 ROWS;





