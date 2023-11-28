import re
import time
from collections import defaultdict


def execute_with_log(cursor, query, log):
    """
    Execute `query` with `connection` while logging SQL, timing and IO information


    """
    connection = cursor.connection
    log.info(f"SQL:\n{query}")

    # https://pymssql.readthedocs.io/en/stable/ref/_mssql.html#_mssql.MSSQLConnection.set_msghandler
    messages = []
    connection._conn.set_msghandler(lambda *args: messages.append(args[-1]))
    cursor.execute("SET STATISTICS TIME ON")
    cursor.execute("SET STATISTICS IO ON")
    start = time.monotonic()

    # Actually run the query
    cursor.execute(query)

    duration = time.monotonic() - start
    timings, table_io = parse_statistics_messages(messages)

    if table_io:
        log.info(format_table_io(table_io))

    # In order to make the logs visually parseable rather than just a wall of text we
    # want some visual space between logs for each query. The simplest way to achieve
    # this is to append some newlines to the last thing we log here.
    append_str_to_last_value(timings, "\n\n")
    log.info(f"{int(duration)} seconds:", **timings)


SQLSERVER_STATISTICS_REGEX = re.compile(
    rb"""
    .* (

    # Regex to match timing statistics messages

    SQL\sServer\s
      (?P<timing_type>parse\sand\scompile\stime|Execution\sTime)
    .* CPU\stime\s=\s(?P<cpu_ms>\d+)\sms
    .* elapsed\stime\s=\s(?P<elapsed_ms>\d+)\sms

    |

    # Regex to match IO statistics messages

    Table\s'(?P<table>[^']+)'. \s+
    Scan\scount\s (?P<scans>\d+), \s+
    logical\sreads\s (?P<logical>\d+), \s+
    physical\sreads\s (?P<physical>\d+), \s+
    read-ahead\sreads\s (?P<read_ahead>\d+), \s+
    lob\slogical\sreads\s (?P<lob_logical>\d+), \s+
    lob\sphysical\sreads\s (?P<lob_physical>\d+), \s+
    lob\sread-ahead\sreads\s (?P<lob_read_ahead>\d+)

    ) .*
    """,
    flags=re.DOTALL | re.VERBOSE,
)


def parse_statistics_messages(messages):
    """
    Accepts a list of MSSQL statistics messages and returns a dict of cumulative timing
    stats and a dict of cumulative table IO stats
    """
    timings = {
        "exec_cpu_ms": 0,
        "exec_elapsed_ms": 0,
        "exec_cpu_ratio": 0.0,
        "parse_cpu_ms": 0,
        "parse_elapsed_ms": 0,
    }
    table_io = defaultdict(
        lambda: {
            "scans": 0,
            "logical": 0,
            "physical": 0,
            "read_ahead": 0,
            "lob_logical": 0,
            "lob_physical": 0,
            "lob_read_ahead": 0,
        }
    )
    timing_types = {b"parse and compile time": "parse", b"Execution Time": "exec"}
    for message in messages:
        if match := SQLSERVER_STATISTICS_REGEX.match(message):
            if timing_type := match["timing_type"]:
                prefix = timing_types[timing_type]
                timings[f"{prefix}_cpu_ms"] += int(match["cpu_ms"])
                timings[f"{prefix}_elapsed_ms"] += int(match["elapsed_ms"])
            elif table := match["table"]:
                table = table.decode(errors="ignore")
                # Temporary table names are, internally to MSSQL, made globally unique
                # by padding with underscores and appending a unique suffix. We need to
                # restore the original name so our stats make sense. If you've got an
                # actual temp table name with 5 underscores in it you deserve everything
                # you get.
                if table.startswith("#"):
                    table = table.partition("_____")[0]
                stats = table_io[table]
                for key in stats.keys():
                    stats[key] += int(match[key])
            else:
                # Given the structure of the regex it shouldn't be possible to get here,
                # but if somehow we did I'd rather drop the stats message than blow up
                pass  # pragma: no cover
    if timings["exec_elapsed_ms"] != 0:
        timings["exec_cpu_ratio"] = round(
            timings["exec_cpu_ms"] / timings["exec_elapsed_ms"], 2
        )
    return timings, table_io


def format_table_io(table_io):
    results_table = table_io_dict_to_table(table_io)
    return format_table(results_table)


def table_io_dict_to_table(table_io):
    headers = list(table_io.values())[0].keys()
    table = [[*headers, "table"]]
    for table_name, stats in table_io.items():
        table.append(
            [*(str(stats[header]) for header in headers), table_name],
        )
    return table


def format_table(table):
    column_max_length = {i: 0 for i in range(0, len(table[0]))}
    for row in table:
        # Ignore the right-most column as we don't want to pad that
        for i, value in enumerate(row[:-1]):
            column_max_length[i] = max(column_max_length[i], len(value))
    return "\n".join(
        " ".join(value.ljust(column_max_length[i]) for i, value in enumerate(row))
        for row in table
    )


def append_str_to_last_value(dictionary, suffix):
    last_key, last_value = list(dictionary.items())[-1]
    dictionary[last_key] = f"{last_value}{suffix}"
