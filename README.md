# OpenSAFELY SQL Runner

SQL Runner allows a platform developer to run SQL against a backend,
for data development projects.
Its use is governed by the [platform developer access policy](https://docs.opensafely.org/developer-access-policy/).

## Type One Opt Out data

Unless your data development project has permission to use Type One Opt Out (T1OO) data,
you should either exclude these data or explain why you haven't excluded them in a
comment.

To exclude T1OO data, for example:

```sql
SELECT <select_list>
FROM Patient
WHERE Patient_ID NOT IN (SELECT Patient_ID FROM PatientsWithTypeOneDissent)
GROUP BY <group_by_clause>
ORDER BY <order_by_expression>
```

To explain why T1OO data haven't been excluded, for example:

```sql
-- This query is for a data development project that must include T1OO data.
-- Consequently, this query doesn't reference the PatientsWithTypeOneDissent table.
SELECT <select_list>
FROM Patient
GROUP BY <group_by_clause>
ORDER BY <order_by_expression>
```

## Notes for developers

Please see [_DEVELOPERS.md_](DEVELOPERS.md).
