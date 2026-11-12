# Conditional processing (processor `condition` key)

Source: https://docs.fluentbit.io/manual/data-pipeline/processors/conditional-processing
Note for Spec authors. Not a plugin entry; the catalogue schema has no representation for it yet.

## Minimum version

> Conditional processing is available in Fluent Bit version 4.0 and greater.

## Restrictions (quoted)

> * Only YAML configuration files support processors, including conditional processors.
> * Conditional processing isn't supported if you're using a filter as a processor.

So `condition` applies only to native processors (e.g. `content_modifier`) under `processors.logs`, not to filters attached as processors (`as_processor: true` filters). The page's examples use `logs` processors only.

## Syntax (quoted)

> You can turn a standard processor into a conditional processor by adding a `condition` block to the processor's YAML configuration settings.

```yaml
pipeline:
  inputs:
    <...>

  processors:
    logs:
      - name: processor_name
        <...>
        condition:
          op: {and|or}
          rules:
          - field: {field_name1}
            op: {comparison_operator}
            value: {comparison_value1}
          - field: {field_name2}
            op: {comparison_operator}
            value: {comparison_value2}
        <...>
```

> Each processor can only have a single `condition` block, but that condition can include multiple rules. These rules are stored as items in the `condition.rules` array.

## `condition.op`

* `and`: a log entry meets the condition when all the rules in `condition.rules` are truthy.
* `or`: a log entry meets the condition when one or more rules in `condition.rules` are truthy.

## Rules (`condition.rules[]`)

Each item must include:

| Parameter | Description (quoted) |
| --- | --- |
| `field` | The field within your logs to evaluate. The value of this parameter must use the correct syntax to access the fields inside logs. |
| `op` | The comparison operator to evaluate whether the rule is true. This parameter (`condition.rules.op`) is distinct from the `condition.op` parameter and has different possible values. |
| `value` | The value of the specified log field to use in your comparison. Optionally, you can provide an array that contains multiple values. |

### Field access (record accessor)

> The `conditions.rules.field` parameter uses record accessor syntax to reference fields inside logs.
> You can use `$field` syntax to access a top-level field, and `$field['child']['subchild']` to access nested fields.

In YAML the accessor is written as a quoted string, e.g. `"$status"`, `"$request['method']"`.

### Comparison operators (`condition.rules.op`)

* `eq`: equal to
* `neq`: not equal to
* `gt`: greater than
* `lt`: less than
* `gte`: greater than or equal to
* `lte`: less than or equal to
* `regex`: matches a regular expression
* `not_regex`: doesn't match a regular expression
* `in`: is included in the specified array
* `not_in`: isn't included in the specified array

`in` / `not_in` take an array for `value` (e.g. `["POST", "PUT", "DELETE"]`). The other operators take a scalar (strings and numbers appear in the examples, e.g. `value: 200`, `value: "POST"`).

## Complete examples (copied from the page)

### Multiple conditions with `and`

```yaml
pipeline:
  inputs:
    - name: dummy
      dummy: '{"request": {"method": "POST", "path": "/api/v1/sensitive-data"}}'
      tag: request.log

      processors:
          logs:
            - name: content_modifier
              action: insert
              key: requires_audit
              value: true
              condition:
                op: and
                rules:
                  - field: "$request['method']"
                    op: eq
                    value: "POST"
                  - field: "$request['path']"
                    op: regex
                    value: "\/sensitive-.*"
```

### Array of values (`in`)

```yaml
pipeline:
  inputs:
    - name: dummy
      dummy: '{"request": {"method": "GET", "path": "/api/v1/resource"}}'
      tag: request.log

      processors:
        logs:
          - name: content_modifier
            action: insert
            key: high_priority_method
            value: true
            condition:
              op: and
              rules:
                - field: "$request['method']"
                  op: in
                  value: ["POST", "PUT", "DELETE"]
```

### Multiple conditions with `or`

```yaml
pipeline:
  inputs:
    - name: dummy
      dummy: '{"request": {"method": "GET", "path": "/api/v1/resource", "status_code": 200, "response_time": 150}}'
      tag: request.log

      processors:
        logs:
          - name: content_modifier
            action: insert
            key: requires_performance_check
            value: true
            condition:
              op: or
              rules:
                - field: "$request['response_time']"
                  op: gt
                  value: 100
                - field: "$request['status_code']"
                  op: gte
                  value: 400
```

### Multiple processors, each with its own condition

```yaml
pipeline:
  inputs:
    - name: dummy
      dummy: '{"log": "Error: Connection refused", "level": "error", "service": "api-gateway"}'
      tag: app.log

      processors:
        logs:
          - name: content_modifier
            action: insert
            key: alert
            value: true
            condition:
              op: and
              rules:
                - field: "$level"
                  op: eq
                  value: "error"
                - field: "$service"
                  op: in
                  value: ["api-gateway", "authentication", "database"]

          - name: content_modifier
            action: insert
            key: paging_required
            value: true
            condition:
              op: and
              rules:
                - field: "$log"
                  op: regex
                  value: "(?i)(connection refused|timeout|crash)"
                - field: "$level"
                  op: in
                  value: ["error", "fatal"]
```

The page's remaining example (Basic condition) is a single `eq` rule on `"$request['method']"`.
