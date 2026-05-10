# Two Bugs in JSON Schema Inference

## Background: What Is Schema Inference?

Schema inference is the process by which a program **analyzes existing JSON data and automatically builds a schema from it** - a set of rules describing what values are valid within a given structure. This sounds straightforward, but it requires one critical thing: the program must analyze **all of the data**, not just a fragment of it.

---

## Bug 1: Incomplete Type Analysis When Merging Objects From an Array

### What Is the Problem?

Consider an array of objects where the same field takes on different types:

```json
[
  { "cat": "fur" },
  { "cat": 69 }
]
```

A flawed implementation analyzes the first object, registers the type of the `"cat"` field as `string` - and when it encounters the next object, **does not update the already-registered type**, because the key is already known. The resulting schema looks like this:

```json
{ "type": "string" }
```

### Why Is This a Bug?

A schema is meant to describe the **full range of possible data**, not just the first case encountered. The schema generated from the array above should read:

```json
{ "type": ["string", "integer"] }
```

A schema based solely on the first occurrence is **incomplete and incorrect** - validating data against such a schema will reject perfectly valid records simply because the generator did not bother examining the full dataset.

For arrays containing mixed types directly (rather than inside objects), the correct approach is to use `anyOf`:

```json
{
  "type": "array",
  "items": {
    "anyOf": [
      { "type": "string" },
      { "type": "integer" }
    ]
  }
}
```

### Consequences

A schema with a single type where multiple types are required becomes an **active source of errors** in any system that relies on it. A validator built on such a schema will reject valid data - for example, records containing a number instead of a string - treating them as malformed, even though they are fully consistent with the actual data structure. In production environments, this translates to false positives, rejected transactions, or the need for manual review of data that should require no intervention at all.

What makes this particularly insidious is that **the bug is hard to detect**. The schema looks correct, validation runs without exceptions, and the system raises no errors. The problem only surfaces when rejected records start accumulating - and the diagnosis is far from obvious. On the surface it appears that the data does not conform to the schema, rather than that the schema is too narrow to describe the data.

---

## Bug 2: Accepting Duplicate Keys Within an Object

### What Is the Problem?

The JSON standard (RFC 8259) recommends that keys within a single object be unique, though it does not strictly enforce this. A flawed generator implementation **neither detects nor reports duplicate keys**, treating an object such as the following as valid input:

```json
{ "cat": "fur", "cat": 69 }
```

Worse still, it proceeds to build a schema from it - even though the input structure itself is malformed.

### Why Is This a Bug?

An object with a duplicate key represents **data with undefined behavior**. Different parsers handle it differently - some retain the first occurrence, others the last, and some throw an exception outright. There is no guarantee of consistency across environments.

A schema generator that allows such data through without a warning acts like an inspector who certifies a building constructed from contradictory blueprints. The building may stand - but what happens once someone steps inside depends entirely on who built it and how.

### Consequences

Duplicate keys are a class of bug whose consequences are **disproportionately difficult to debug** relative to their apparent harmlessness. The object itself raises no exception - data flows through the system without any warning, until the moment two different components read the same record and receive **different values for the same field**. One parser retains `"fur"`, another retains `69` - and both behave "correctly" according to their own implementation.

In practice, this leads to inconsistencies that are nearly impossible to reproduce in a controlled environment: the bug surfaces only when a specific record reaches a specific component, and its root cause lies not in any business logic, but in the data parsing layer. Issues of this kind can persist in a system for weeks before anyone connects the symptoms to their source.

### How Should It Work?

The generator should **detect duplicate keys at the data ingestion stage** and return an error or warning before it attempts to build a schema at all. Building a schema from malformed input produces a malformed schema - regardless of how sound the rest of the implementation is.

---

## The Common Root of Both Bugs

Both problems stem from the same underlying assumption: that **the first case encountered is sufficient**. In the first bug - the first type encountered. In the second - the first value of a duplicated key. A robust schema generator must treat data as a whole, not as a sequence of individual observations where each subsequent one matters less than the last. In both cases, the consequences are not immediate - which makes them especially dangerous in systems where input data is assumed to be trustworthy.
