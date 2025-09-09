from pyspark.sql import functions as F

# --- Operation registries ---
SCHEMA_OPS = {}
COLUMN_OPS = {}
VALIDATION_OPS = {}

def register_op(kind, name, func):
    if kind == "schema":
        SCHEMA_OPS[name] = func
    elif kind == "column":
        COLUMN_OPS[name] = func
    elif kind == "validation":
        VALIDATION_OPS[name] = func

# --- Example: built-in ops ---
def op_date(df, spec):
    return df.withColumn(spec["name"], F.to_date(F.col(spec["field"])))

register_op("column", "date", op_date)

# --- Example: developer-defined op ---
def op_normalize_currency(df, spec):
    amt = F.col(spec["field"])
    cur = F.col(spec["params"]["currency_field"])
    return df.withColumn(spec["name"], amt * F.when(cur == "USD", 1)
                                         .when(cur == "EUR", 1.1)
                                         .otherwise(1))

register_op("column", "normalize_currency", op_normalize_currency)

# --- Framework apply function ---
def apply_columns(df, columns_config):
    for spec in columns_config:
        op_name = spec["op"]
        if op_name not in COLUMN_OPS:
            raise ValueError(f"Unknown column op: {op_name}")
        df = COLUMN_OPS[op_name](df, spec)
    return df
